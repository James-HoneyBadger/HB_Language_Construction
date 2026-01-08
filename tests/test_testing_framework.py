import pytest
from src.parsercraft.testing_framework import (
    TestCase, TestRunner, TestStatus, AssertionError as MyAssertionError
)

class SampleTest(TestCase):
    def test_pass(self):
        self.assert_equal(1, 1)
        self.assert_true(True)
        self.assert_is_none(None)
    
    def test_fail(self):
        self.assert_equal(1, 2, "Failure msg")
        
    def test_error(self):
        raise ValueError("Oops")

def test_assertions():
    tc = TestCase()
    
    # Success cases
    tc.assert_equal(1, 1)
    tc.assert_not_equal(1, 2)
    tc.assert_true(True)
    tc.assert_false(False)
    tc.assert_is_none(None)
    tc.assert_is_not_none(1)
    tc.assert_in(1, [1, 2])
    tc.assert_greater(2, 1)
    tc.assert_less(1, 2)
    
    def raise_func():
        raise ValueError()
    tc.assert_raises(ValueError, raise_func)
    
    # Fail cases - check MyAssertionError is raised
    with pytest.raises(MyAssertionError):
        tc.assert_equal(1, 2)
        
    with pytest.raises(MyAssertionError):
        tc.assert_true(False)

def test_runner_suite():
    runner = TestRunner(verbose=False)
    suite = runner.run_suite(SampleTest)
    
    assert suite.name == "SampleTest"
    assert len(suite.tests) == 3
    
    # Check results
    passes = [t for t in suite.tests if t.status == TestStatus.PASSED]
    fails = [t for t in suite.tests if t.status == TestStatus.FAILED]
    errors = [t for t in suite.tests if t.status == TestStatus.ERROR]
    
    assert len(passes) == 1
    assert passes[0].test_name == "SampleTest.test_pass"
    
    assert len(fails) == 1
    assert fails[0].test_name == "SampleTest.test_fail"
    assert "Failure msg" in fails[0].error_message
    
    assert len(errors) == 1
    assert errors[0].test_name == "SampleTest.test_error"
    assert "Oops" in errors[0].error_message
