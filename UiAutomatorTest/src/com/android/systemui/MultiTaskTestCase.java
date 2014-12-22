package com.android.systemui;

import java.io.IOException;

import android.os.RemoteException;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class MultiTaskTestCase extends AutomatorTestCase {

    public void testRecycle() throws IOException, InterruptedException,
            UiObjectNotFoundException, RemoteException {
        // 返回主界面
        getUiDevice().pressHome();

        // 打开最近使用的应用程序用户向导
        Process p = Runtime.getRuntime().exec("am start --user 0 -n com.android.systemui/.NubiaRecent.UserGuideActivity");
        p.waitFor();

        // 没有启动完成则按下最近使用应用程序
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.android.systemui"));
        if (validation.waitForExists(3000)) {
            // 点击我知道了
            UiObject hand = new UiObject(new UiSelector().resourceId(
                    "com.android.systemui:id/hand_click"));
            if (hand.exists()) {
                hand.click();
            }
        } else {
            getUiDevice().pressRecentApps();
        }

        // 点击回收并等待消失
        UiObject recycle = new UiObject(new UiSelector().resourceId(
                "com.android.systemui:id/recycle"));
        if (recycle.waitForExists(3000)) {
            recycle.click();
            recycle.waitUntilGone(8000);
        }
    }
}
