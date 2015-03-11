package com.qihoo.appstore;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class AppStoreTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.qihoo.appstore/.activities.LauncherActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.qihoo.appstore"));
        assertTrue(validation.waitForExists(5000));

        UiScrollable guide = new UiScrollable(new UiSelector().resourceId(
                "com.qihoo.appstore:id/guide_viewpager"));
        if (guide.exists()) {
            guide.setAsHorizontalList();
            guide.scrollToEnd(2);
            UiObject finish = new UiObject(new UiSelector().resourceId(
                    "com.qihoo.appstore:id/user_guide_btn"));
            finish.click();
        }

        UiObject title = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/titleIcon"));
        title.click();
        UiObject login = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/login_icon"));
        if (login.exists()) {
            login.click();

            UiObject slide = new UiObject(new UiSelector().resourceId(
                    "com.qihoo.appstore:id/slide_to_right"));
            slide.click();
    
            UiObject username = new UiObject(new UiSelector().resourceId(
                    "com.qihoo.appstore:id/edittext_account"));
            username.setText("18824238317");
            UiObject password = new UiObject(new UiSelector().resourceId(
                    "com.qihoo.appstore:id/edittext_password"));
            password.setText("zte123456");
            UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                    "com.qihoo.appstore:id/button_login"));
            loginbtn.click();
        }
    }
}
