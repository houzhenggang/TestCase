package com.chaozh.iReader;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class ReaderTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.chaozh.iReader/.ui.activity.WelcomeActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.chaozh.iReader"));
        assertTrue(validation.waitForExists(5000));

        UiObject confirm = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/defualt_compoundButton").text("确定"));
        if (confirm.waitForExists(3000)) {
            confirm.click();
        }

        UiScrollable pager = new UiScrollable(new UiSelector().resourceId(
                "com.chaozh.iReader:id/viewpager"));
        if (pager.exists()) {
            pager.setAsHorizontalList();
            pager.scrollToEnd(1);

            UiObject startup = new UiObject(new UiSelector().resourceId(
                    "com.chaozh.iReader:id/btn_start"));
            startup.click();
        }

        UiObject center = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/bookShelf_head_Center_ID"));
        center.click();
        center.click();

        UiObject left = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/bookShelf_head_left_ID"));
        left.click();

        UiObject login = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/person_longin"));
        login.clickAndWaitForNewWindow();

        UiObject ireader = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/account_main_thirdlogin")
                .childSelector(new UiSelector().index(0)
                .childSelector(new UiSelector().index(1)
                .childSelector(new UiSelector().index(1)
                .childSelector(new UiSelector().index(0))))));
        ireader.clickAndWaitForNewWindow();

        UiObject username = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/account_block_zhangyueid_login_name"));
        username.setText("18824238317");
        UiObject password = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/account_block_zhangyueid_login_password"));
        password.setText("ztemt123");
        UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                "com.chaozh.iReader:id/account_block_zhangyueid_login_submit"));
        loginbtn.click();
    }
}
