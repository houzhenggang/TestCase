package com.jingdong.app.mall;

import android.widget.RadioButton;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class JDMallTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.jingdong.app.mall/.MainActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    @Override
    public boolean checkForCondition() {
        UiObject message = new UiObject(new UiSelector().resourceId(
                "android:id/message").textStartsWith("温馨提示"));
        if (message.exists()) {
            UiObject ok = new UiObject(new UiSelector().resourceId(
                    "android:id/button1"));
            try {
                ok.click();
            } catch (UiObjectNotFoundException e) {
                e.printStackTrace();
            }
            return true;
        }
        return super.checkForCondition();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.jingdong.app.mall"));
        assertTrue(validation.waitForExists(5000));

        UiScrollable pager = new UiScrollable(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/viewpager"));
        if (pager.waitForExists(3000)) {
            pager.setAsHorizontalList();
            pager.scrollToEnd(4);

            UiObject startup = new UiObject(new UiSelector().resourceId(
                    "com.jingdong.app.mall:id/btn_experience"));
            startup.click();
        }

        UiObject my = new UiObject(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/bottomMenu").childSelector(
                new UiSelector().className(RadioButton.class).index(4)));
        my.waitForExists(8000);
        my.click();
        my.click();

        UiObject login = new UiObject(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/personal_click_for_login"));
        login.clickAndWaitForNewWindow();

        UiObject username = new UiObject(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/login_input_name"));
        username.setText("18824238317");
        UiObject password = new UiObject(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/login_input_password"));
        password.setText("ztemt123");
        UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                "com.jingdong.app.mall:id/login_comfirm_button"));
        loginbtn.click();
    }
}
