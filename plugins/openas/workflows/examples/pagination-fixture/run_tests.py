"""Run the supplied tests and emit stable evidence for actual pass/fail events."""
import sys
import unittest

import test_pagination


class EvidenceResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln(f"CASE PASS {test.id()}")

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.stream.writeln(f"CASE FAIL {test.id()}")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_pagination)
    result = unittest.TextTestRunner(resultclass=EvidenceResult).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
