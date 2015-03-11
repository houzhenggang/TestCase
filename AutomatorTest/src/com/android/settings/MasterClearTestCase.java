package com.android.settings;

import android.os.Build;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
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
        if (Build.MODEL.equals("Nexus 5")) {
            UiObject settings = new UiObject(new UiSelector().resourceId(
                    "android:id/action_bar").childSelector(new UiSelector().index(0)));
            boolean isChinese = settings.getText().equals("设置");
            UiScrollable list = new UiScrollable(new UiSelector().scrollable(true));
            UiObject reset = list.getChildByText(new UiSelector().className(
                    TextView.class), isChinese ? "备份和重置" : "Backup & reset");
            reset.clickAndWaitForNewWindow();
            UiObject title = new UiObject(new UiSelector().text(
                    isChinese ? "恢复出厂设置" : "Factory data reset"));
            title.clickAndWaitForNewWindow();
            UiObject resetPhone = new UiObject(new UiSelector().className(
                    Button.class).text(isChinese ? "恢复手机出厂设置" : "Reset phone"));
            resetPhone.clickAndWaitForNewWindow();
            UiObject eraseEverything = new UiObject(new UiSelector().className(
                    Button.class).text(isChinese ? "清除全部内容" : "Erase everything"));
            eraseEverything.click();
        } else {
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
            UiObject list = new UiObject(new UiSelector().className(ListView.class));
            for (int i = 0; i < list.getChildCount(); i++) {
                UiObject ll = list.getChild(new UiSelector().className(
                        LinearLayout.class).index(i));
                UiObject tv = ll.getChild(new UiSelector().className(
                        TextView.class).index(0));
                if (tv.getText().matches("^(格式化手机存储|删除应用程序)$")) {
                    UiObject cb = ll.getChild(new UiSelector().resourceId(
                            "android:id/checkbox"));
                    if (cb.isCheckable() && !cb.isChecked()) {
                        cb.click();
                    }
                }
            }
            UiObject reset = new UiObject(new UiSelector().resourceId(
                    "com.android.settings:id/btn_reset_master_clear"));
            reset.click();
            UiObject confirm = new UiObject(new UiSelector().text("确认重置"));
            confirm.click();
        }
    }
}
