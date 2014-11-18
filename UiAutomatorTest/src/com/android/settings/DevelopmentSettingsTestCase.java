package com.android.settings;

import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class DevelopmentSettingsTestCase extends UiAutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testKeepScreenOn() throws UiObjectNotFoundException {
        UiObject list = new UiObject(new UiSelector().className(ListView.class));
        for (int i = 0; i < list.getChildCount(); i++) {
            UiObject ll = list.getChild(new UiSelector().className(
                    LinearLayout.class).index(i));
            UiObject tv = ll.getChild(new UiSelector().className(
                    TextView.class).index(0));
            if (tv.getText().equals("不锁定屏幕")) {
                UiObject cb = ll.getChild(new UiSelector().resourceId(
                        "android:id/checkbox"));
                if (cb.isCheckable() && !cb.isChecked()) {
                    cb.click();
                }
                break;
            }
        }
    }

    public void testTrackFrameTimeDumpsysGfxinfo() throws UiObjectNotFoundException {
        String text = "adb shell dumpsys gfxinfo";
        UiScrollable list = new UiScrollable(new UiSelector().className(ListView.class));
        list.setAsVerticalList();
        UiObject item = list.getChildByText(new UiSelector().resourceId(
                "android:id/title"), "GPU 呈现模式分析", true);
        item.click();
        UiObject option = new UiObject(new UiSelector().textContains(text));
        option.click();
    }
}
