"""Test runner for exception handling transform test cases.

The transform inserts exception handling branch operations to IR.
"""

import os.path
from typing import List

from mypy.test.config import test_temp_dir
from mypy.test.data import parse_test_cases, DataDrivenTestCase, DataSuite
from mypy.errors import CompileError

from mypyc.ops import format_func
from mypyc.exceptions import insert_exception_handling
from mypyc.refcount import insert_ref_count_opcodes
from mypyc.test.testutil import (
    ICODE_GEN_BUILTINS,
    build_ir_for_single_file,
    use_custom_builtins,
    MypycDataSuite,
    assert_test_output,
)
from mypyc.test.config import test_data_prefix

files = [
    'exceptions.test'
]


class TestExceptionTransform(MypycDataSuite):
    files = files
    base_path = test_temp_dir

    def run_case(self, testcase: DataDrivenTestCase) -> None:
        """Perform a reference count opcode insertion transform test case."""

        with use_custom_builtins(os.path.join(test_data_prefix, ICODE_GEN_BUILTINS), testcase):
            try:
                ir = build_ir_for_single_file(testcase.input)
            except CompileError as e:
                actual = e.messages
            else:
                # Expect one function + module top level function.
                assert len(ir) == 2, "Only 1 function definition expected per test case"
                fn = ir[0]
                insert_exception_handling(fn)
                insert_ref_count_opcodes(fn)
                actual = format_func(fn)
                actual = actual[actual.index('L0:'):]

            assert_test_output(testcase, actual, 'Invalid source code output')
