import datetime
import json
import logging
import sys
import time
import urllib
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')


class QuipClient(object):
    """A Quip API client"""
    # Edit operations
    APPEND, \
    PREPEND, \
    AFTER_SECTION, \
    BEFORE_SECTION, \
    REPLACE_SECTION, \
    DELETE_SECTION = range(6)

    def __init__(self, access_token=None, base_url=None,
                 request_timeout=None, retry_rate_limit=False):
        """Constructs a Quip API client.
        If `access_token` is given, all of the API methods in the client
        will work to read and modify Quip documents.
        Otherwise, only `get_authorization_url` and `get_access_token`
        work, and we assume the client is for a server using the Quip API's
        OAuth endpoint.
        """
        self.access_token = access_token
        self.base_url = base_url if base_url else "https://platform.quip.com"
        self.request_timeout = request_timeout if request_timeout else 10
        self.retry_rate_limit = retry_rate_limit

    def get_folder(self, id):
        """Returns the folder with the given ID."""
        return self._fetch_json("folders/" + id)

    def get_messages(self, thread_id, max_created_usec=None, count=None):
        """Returns the most recent messages for the given thread.
        To page through the messages, use max_created_usec, which is the
        sort order for the returned messages.
        count should be an integer indicating the number of messages you
        want returned. The maximum is 100.
        """
        return self._fetch_json(
            "messages/" + thread_id, max_created_usec=max_created_usec,
            count=count)

    def get_thread(self, id):
        """Returns the thread with the given ID."""
        return self._fetch_json("threads/" + id)

    def new_document(self, content, format="html", title=None, member_ids=[]):
        """Creates a new document from the given content.
        To create a document in a folder, include the folder ID in the list
        of member_ids, e.g.,
            client = quip.QuipClient(...)
            user = client.get_authenticated_user()
            client.new_document(..., member_ids=[user["archive_folder_id"]])
        """
        return self._fetch_json("threads/new-document", post_data={
            "content": content,
            "format": format,
            "title": title,
            "member_ids": ",".join(member_ids),
        })

    def edit_document(self, thread_id, content, operation=APPEND, format="html",
                      section_id=None):#, **kwargs):
        """Edits the given document, adding the given content.
        `operation` should be one of the constants described above. If
        `operation` is relative to another section of the document, you must
        also specify the `section_id`.
        """
        args = {
            "thread_id": thread_id,
            "content": content,
            "location": operation,
            "format": format,
            "section_id": section_id,
        }
        #args.update(kwargs)
        return self._fetch_json("threads/edit-document", post_data=args)

    def _fetch_json(self, path, post_data=None, **args):
        request = urllib2.Request(url=self._url(path, **args))
        if post_data:
            post_data = dict((k, v) for k, v in post_data.items()
                             if v or isinstance(v, int))
            request.data = urllib.urlencode(self._clean(**post_data))
        if self.access_token:
            request.add_header("Authorization", "Bearer " + self.access_token)
        try:
            return json.loads(
                urllib2.urlopen(request, timeout=self.request_timeout).read())
        except urllib2.HTTPError, error:
            try:
                # Extract the developer-friendly error message from the response
                message = json.loads(error.read())["error_description"]
            except Exception:
                raise error
            if (self.retry_rate_limit and error.code == 503 and
                message == "Over Rate Limit"):
                # Retry later.
                reset_time = float(error.headers.get("X-RateLimit-Reset"))
                delay = max(2, reset_time - time.time() + 1)
                logging.warning("Rate Limit, delaying for %d seconds" % delay)
                time.sleep(delay)
                return self._fetch_json(path, post_data, **args)
            else:
                raise QuipError(error.code, message, error)

    def _clean(self, **args):
        # We only expect ints or strings, but on Windows ints can become longs
        return dict((k, str(v) if isinstance(
            v, (int, float, long, complex)) else v.encode("utf-8"))
                    for k, v in args.items() if v or isinstance(
                            v, (int, float, long, complex)))

    def _url(self, path, **args):
        url = self.base_url + "/1/" + path
        args = self._clean(**args)
        if args:
            url += "?" + urllib.urlencode(args)
        return url


class QuipError(Exception):
    def __init__(self, code, message, http_error):
        Exception.__init__(self, "%d: %s" % (code, message))
        self.code = code
        self.http_error = http_error
