from django.test.runner import DiscoverRunner


class SrcDiscoverRunner(DiscoverRunner):
    """
    Make default discovery compatible with src-based layout.
    """

    def build_suite(self, test_labels=None, **kwargs):
        labels = test_labels or ["apps", "tests"]
        return super().build_suite(test_labels=labels, **kwargs)
