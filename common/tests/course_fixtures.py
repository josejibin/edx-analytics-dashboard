import uuid


class CourseStructureAPIFixtureMixin(object):
    """Represents a course that can serialize itself in the form generated by the Course Structure API."""
    def __init__(self, *args, **kwargs):
        self._uuid = uuid.uuid4().hex
        self._type = None
        self._display_name = kwargs.get('display_name', '')
        self._graded = False
        self._assignment_type = None
        self._children = []
        # Course data
        self._org = None
        self._course = None
        self._run = None

    def to_dict(self):
        """Return a dict representation of this block in the form generated by the Course Structure API."""
        return {
            'id': self.id,
            'type': self._type,
            'display_name': self._display_name,
            'graded': self._graded,
            'format': self._assignment_type,
            'children': [child.id for child in self._children]
        }

    def add_children(self, *children):
        """Add children to this block"""
        self._children += children
        return self

    def pre_order(self):
        """Return the fixture rooted at `self` as a list visited in pre-order."""
        visited = [self]
        for child in self._children:
            # Children should inherit and cache org, course, and run for ID generation.
            # 'graded' is also inherited.
            child._org = self._org
            child._course = self._course
            child._run = self._run
            child._graded = self._graded
            visited += child.pre_order()
        return visited

    @property
    def id(self):
        """Uniquely identifies this block in the format used by the Course Structure API."""
        return 'i4x://{org}/{course}/{type}/{_uuid}'.format(
            org=self._org, course=self._course, type=self._type, _uuid=self._uuid
        )


class CourseFixture(CourseStructureAPIFixtureMixin):
    """Represents a course as returned by the Course Structure API."""
    def __init__(self, org=None, course=None, run=None, *args, **kwargs):
        super(CourseFixture, self).__init__(*args, **kwargs)
        self._type = 'course'
        self._org = org
        self._course = course
        self._run = run
        self._uuid = run  # The org/course/run triple uniquely identifies the course

    def course_structure(self):
        """Return a dict representing this course in the form generated by the Course Structure API."""
        return {
            'root': self.id,
            'blocks': {
                child.id: child.to_dict()
                for child in self.pre_order()
            }
        }


class ChapterFixture(CourseStructureAPIFixtureMixin):
    """Represents a chapter as returned by the Course Structure API."""
    def __init__(self, *args, **kwargs):
        super(ChapterFixture, self).__init__(*args, **kwargs)
        self._type = 'chapter'


class SequentialFixture(CourseStructureAPIFixtureMixin):
    """Represents a sequential as returned by the Course Structure API."""
    def __init__(self, graded=False, assignment_type=None, *args, **kwargs):
        super(SequentialFixture, self).__init__(*args, **kwargs)
        self._graded = graded
        self._assignment_type = assignment_type
        self._type = 'sequential'


class VerticalFixture(CourseStructureAPIFixtureMixin):
    """Represents a vertical as returned by the Course Structure API."""
    def __init__(self, *args, **kwargs):
        super(VerticalFixture, self).__init__(*args, **kwargs)
        self._type = 'vertical'


class VideoFixture(CourseStructureAPIFixtureMixin):
    """Represents a video as returned by the Course Structure API."""
    def __init__(self, *args, **kwargs):
        super(VideoFixture, self).__init__(*args, **kwargs)
        self._type = 'video'
