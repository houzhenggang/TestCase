package com.Qunar;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class QunarTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.Qunar/.NoteActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName("com.Qunar"));
        assertTrue(validation.waitForExists(5000));

        UiObject gotonext = new UiObject(new UiSelector().resourceId(
                "com.Qunar:id/button1"));
        if (gotonext.exists()) {
            gotonext.click();
        }

        UiObject usercenter = new UiObject(new UiSelector().resourceId(
                "com.Qunar:id/mod_usercenter"));
        usercenter.waitForExists(5000);
        usercenter.click();
        usercenter.click();

        UiObject username = new UiObject(new UiSelector().resourceId(
                "com.Qunar:id/et_username"));
        username.setText("18824238317");
        UiObject password = new UiObject(new UiSelector().resourceId(
                "com.Qunar:id/et_password"));
        password.setText("ztemt123");
        UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                "com.Qunar:id/uc_login_btn"));
        loginbtn.click();
    }
}
