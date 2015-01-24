package com.android.settings;

import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class MasterClearTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        Process p = Runtime.getRuntime().exec("am start --user 0 -a android.settings.SETTINGS");
        p.waitFor();
    }

    public void testMasterClear() throws UiObjectNotFoundException {
        UiObject other = new UiObject(new UiSelector().className(
                TextView.class).text("其他"));
        if (!other.exists()) {
            UiScrollable list = new UiScrollable(new UiSelector().scrollable(true));
            other = list.getChildByText(new UiSelector().className(
                    TextView.class), "其他");
        }
        other.clickAndWaitForNewWindow();
        UiObject title = new UiObject(new UiSelector().text("恢复出厂设置"));
        title.clickAndWaitForNewWindow();
        title = new UiObject(new UiSelector().resourceId(
                "android:id/title").text("恢复出厂设置"));
        title.clickAndWaitForNewWindow();
        UiObject reset = new UiObject(new UiSelector().resourceId(
                "com.android.settings:id/btn_reset_master_clear"));
        reset.click();
        UiObject confirm = new UiObject(new UiSelector().text("确认重置"));
        confirm.click();
    }
}
