from analyticsclient.exceptions import NotFoundError
from ddt import ddt, data
from django.core.urlresolvers import reverse
from django.test import TestCase
import mock

from courses.tests.test_views import ViewTestMixin, DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID
from courses.tests.utils import convert_list_of_dicts_to_csv, get_mock_api_enrollment_geography_data, \
    get_mock_api_enrollment_data, get_mock_api_course_activity


@ddt
# pylint: disable=abstract-method
class CourseCSVTestMixin(ViewTestMixin):
    client = None
    column_headings = None
    base_file_name = None

    def assertIsValidCSV(self, course_id, csv_data):
        response = self.client.get(self.path(course_id))

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        csv_prefix = u'edX-DemoX-Demo_2014' if course_id == DEMO_COURSE_ID else u'edX-DemoX-Demo_Course'
        filename = '{0}--{1}.csv'.format(csv_prefix, self.base_file_name)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, csv_data)

    def assertResponseContentType(self, response, content_type):
        self.assertEqual(response['Content-Type'], content_type)

    def assertResponseFilename(self, response, filename):
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{0}"'.format(filename))

    def _test_csv(self, course_id, csv_data):
        with mock.patch(self.api_method, return_value=csv_data):
            self.assertIsValidCSV(course_id, csv_data)

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_response_no_data(self, course_id):
        # Create an "empty" CSV that only has headers
        csv_data = convert_list_of_dicts_to_csv([], self.column_headings)
        self._test_csv(course_id, csv_data)

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_response(self, course_id):
        csv_data = self.get_mock_data(course_id)
        csv_data = convert_list_of_dicts_to_csv(csv_data)
        self._test_csv(course_id, csv_data)

    def test_404(self):
        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        path = reverse(self.viewname, kwargs={'course_id': course_id})

        with mock.patch(self.api_method, side_effect=NotFoundError):
            response = self.client.get(path, follow=True)
            self.assertEqual(response.status_code, 404)


class CourseEnrollmentByCountryCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv_enrollment_by_country'
    column_headings = ['count', 'country', 'course_id', 'date']
    base_file_name = 'enrollment-location'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_geography_data(course_id)


class CourseEnrollmentCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv_enrollment'
    column_headings = ['count', 'course_id', 'date']
    base_file_name = 'enrollment'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_data(course_id)


class CourseEngagementActivityTrendCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv_engagement_activity_trend'
    column_headings = ['any', 'attempted_problem', 'course_id', 'interval_end', 'interval_start',
                       'played_video', 'posted_forum']
    base_file_name = 'engagement-activity'
    api_method = 'analyticsclient.course.Course.activity'

    def get_mock_data(self, course_id):
        return get_mock_api_course_activity(course_id)
