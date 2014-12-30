package com.android.systemui;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class NotificationTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        getUiDevice().pressHome();
        getUiDevice().openNotification();

        // open quick settings panel
        UiObject header = new UiObject(new UiSelector().resourceId(
                "com.android.systemui:id/header"));
        header.click();
    }

    public void testClickRecycle() throws UiObjectNotFoundException {
        UiObject panel = new UiObject(new UiSelector().resourceId(
                "com.android.systemui:id/quick_settings_panel"));
        UiObject recycle = panel.getChild(new UiSelector().resourceId(
                "android:id/title").text("一键清除"));
        if (recycle.exists()) {
            recycle.click();
        }
    }
}
