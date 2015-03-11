package cn.nubia.accounts;

import android.widget.Button;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class NubiaAccountTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n cn.nubia.accounts/.AccountIntroActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "cn.nubia.accounts"));
        assertTrue(validation.waitForExists(5000));

        UiObject login = new UiObject(new UiSelector().className(
                Button.class).text("登录"));
        login.clickAndWaitForNewWindow();

        UiObject username = new UiObject(new UiSelector().resourceId(
                "cn.nubia.accounts:id/username"));
        username.setText("18824238317");
        UiObject password = new UiObject(new UiSelector().resourceId(
                "cn.nubia.accounts:id/password"));
        password.setText("ztemt123");
        UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                "cn.nubia.accounts:id/login"));
        loginbtn.click();

        UiObject gotonext = new UiObject(new UiSelector().resourceId(
                "android:id/button1"));
        if (gotonext.waitForExists(3000)) {
            gotonext.click();
        }
    }
}
