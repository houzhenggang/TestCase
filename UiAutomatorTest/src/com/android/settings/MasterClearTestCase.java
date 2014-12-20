package com.android.settings;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class MasterClearTestCase extends UiAutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        Process p = Runtime.getRuntime().exec("am start --user 0 -a android.settings.SETTINGS");
        p.waitFor();
    }

    public void testMasterClear() throws UiObjectNotFoundException {
        UiScrollable list = new UiScrollable(
                new UiSelector().resourceId("android:id/list"));
        UiObject other = list.getChildByText(
                new UiSelector().resourceId("android:id/title"), "其他");
        other.clickAndWaitForNewWindow();
        UiObject title = new UiObject(new UiSelector().resourceId(
                "android:id/title").text("恢复出厂设置"));
        title.clickAndWaitForNewWindow();
        title.clickAndWaitForNewWindow();
        UiObject reset = new UiObject(new UiSelector().resourceId(
                "com.android.settings:id/btn_reset_master_clear"));
        reset.click();
        UiObject confirm = new UiObject(new UiSelector().resourceId(
                "android:id/button1"));
        confirm.click();
    }
}
