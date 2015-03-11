package com.sina.weibo;

import android.widget.Button;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class WeiboTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.sina.weibo/.SplashActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.sina.weibo"));
        assertTrue(validation.waitForExists(5000));

        UiObject confirm = new UiObject(new UiSelector().className(
                Button.class).text("确定"));
        if (confirm.exists()) {
            confirm.click();
        }

        UiObject login = new UiObject(new UiSelector().className(
                TextView.class).text("登录"));
        if (login.waitForExists(8000)) {
            login.clickAndWaitForNewWindow();

            UiObject username = new UiObject(new UiSelector().resourceId(
                    "com.sina.weibo:id/etLoginUsername"));
            username.click();
            UiObject usertips = new UiObject(new UiSelector().resourceId(
                    "com.sina.weibo:id/login_user_tips_btn"));
            if (usertips.exists()) {
                usertips.click();
            }
            username.setText("2829302503@qq.com");
            UiObject password = new UiObject(new UiSelector().resourceId(
                    "com.sina.weibo:id/etPwd"));
            password.setText("ztemt123");

            UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                    "com.sina.weibo:id/bnLogin"));
            loginbtn.click();
        }
    }
}
