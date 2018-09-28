#!/usr/bin/env python3
# -*-coding:utf-8-*-

import pytest
import allure

from utils.LogTool import Logger


@allure.feature("TestModule1")
class TestTemplate(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()
        cls.logger.info("")
        cls.logger.info("*** The setup class method.")

    @allure.step("+++ teardown class +++")
    def teardown_class(cls):
        cls.logger.info("*** The teardown class method.")
        cls.logger.info("")
        cls.logger = None

    @allure.step("+++ setup method +++")
    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")  # blocker, critical, normal, minor, trivial
    @allure.story("TestFunction1")
    @allure.testcase("TestCase1")
    @pytest.mark.parametrize("param1, param2, result",
                             [('p1v1', 'p2v1', 'r1'), ('p1v2', 'p2v2', 'r2'), ('p1v3', 'p2v3', 'r3')],
                             ids=["TestCase1", "TestCase2", "TestCase3"])
    def test_method1(self, param1, param2, result):
        """ Test check point1.
        :param param1: first param.
        :param param2: second param.
        :param result: expect result.
        """
        self.logger.info(".... Start test method1 ....")
        with allure.step("teststep1: get parameters."):
            allure.attach("params value", "param1: {0}, param2: {1}, result: {2}".format(param1, param2, result))
            self.logger.info("param1: {0}, param2: {1}, result: {2}".format(param1, param2, result))

        with allure.step("teststep2: test the parameters."):
            allure.attach("temp value", "record the temp test values.")
            self.logger.info("record the temp test values.")

        with allure.step("teststep3: assert the test result"):
            allure.attach("期望结果：", "expect result")
            allure.attach("实际结果：", result)
            self.logger.info("assert params result")
            assert True
        self.logger.info(".... End test method1 ....")


if __name__ == '__main__':
    pytest.main(['-s', 'test_template.py'])
