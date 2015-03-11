package com.baidu.tieba;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class TiebaTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.baidu.tieba/.LogoActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.baidu.tieba"));
        assertTrue(validation.waitForExists(5000));

        UiObject login = new UiObject(new UiSelector().resourceId(
                "com.baidu.tieba:id/guide_login"));
        if (login.waitForExists(3000)) {
            login.clickAndWaitForNewWindow();

            UiObject normal = new UiObject(new UiSelector().resourceId(
                    "com.baidu.tieba:id/normal_login"));
            normal.click();

            UiObject username = new UiObject(new UiSelector().resourceId(
                    "com.baidu.tieba:id/login_edit_account"));
            username.setText("18824238317");
            UiObject password = new UiObject(new UiSelector().resourceId(
                    "com.baidu.tieba:id/login_edit_password"));
            password.setText("ztemt123");
            UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                    "com.baidu.tieba:id/text_login"));
            loginbtn.click();
        }
    }
}
