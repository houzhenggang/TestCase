package com.qihoo.appstore;

import android.widget.ListView;
import android.widget.ScrollView;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class QihooAppstoreTestCase extends UiAutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start -n com.qihoo.appstore/.activities.MainActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();

        sleep(3000);
    }

    public void testDisableDownloadAppAutoInstall() throws UiObjectNotFoundException {
        getUiDevice().pressMenu();
        UiObject settings = new UiObject(new UiSelector().text("设置"));
        settings.click();

        UiScrollable list = new UiScrollable(new UiSelector().className(ScrollView.class));
        list.getChildByText(new UiSelector().resourceId(
                "com.qihoo.appstore:id/title"), "下载完提示安装", true);
        UiObject cb = list.getChild(new UiSelector().resourceId(
                "com.qihoo.appstore:id/pref_download_app_auto_install_checkbox"));
        if (cb.isSelected()) {
            cb.click();
        }

        UiObject title = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/titleText"));
        title.click();
    }

    public void testDisableDeleteDownfile() throws UiObjectNotFoundException {
        getUiDevice().pressMenu();
        UiObject settings = new UiObject(new UiSelector().text("设置"));
        settings.click();

        UiScrollable list = new UiScrollable(new UiSelector().className(ScrollView.class));
        list.getChildByText(new UiSelector().resourceId("com.qihoo.appstore:id/title"),
                "删除安装源文件", true);
        UiObject cb = list.getChild(new UiSelector().resourceId(
                "com.qihoo.appstore:id/pre_delete_installed_downfile_tip_checkbox"));
        if (cb.isSelected()) {
            cb.click();
        }

        UiObject title = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/titleText"));
        title.click();
    }

    public void testDownloadTop10Apk() throws UiObjectNotFoundException {
        // 进入软件榜单
        UiObject soft = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/bottom_txt").text("软件"));
        soft.click();
        UiObject list = new UiObject(new UiSelector().text("榜单"));
        list.click();
        sleep(8000);
        UiObject pick = new UiObject(new UiSelector().text("精选"));
        pick.click();
        list.click();

        // 下载前10的软件
        UiScrollable softs = new UiScrollable(new UiSelector().className(
                ListView.class).index(1));
        if (softs.waitForExists(30000)) {
            for (int i = 0; i < Math.min(5, softs.getChildCount()); i++) {
                UiObject item = softs.getChild(new UiSelector().index(i)
                        .childSelector(new UiSelector().description(
                                String.valueOf(i + 1))));
                UiObject button = item.getFromParent(new UiSelector()
                        .descriptionMatches("下载 Link|继续 Link"));
                if (button.exists()) {
                    button.click();
                }
            }
        }

        // 进入游戏榜单
        UiObject game = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/bottom_txt").text("游戏"));
        game.click();
        list.click();
        sleep(8000);
        pick.click();
        list.click();

        // 下载前10的游戏
        UiScrollable games = new UiScrollable(new UiSelector().className(
                ListView.class).index(1));
        assertTrue("Unable to load games", games.waitForExists(30000));
        for (int i = 0; i < Math.min(5, games.getChildCount()); i++) {
            UiObject item = games.getChild(new UiSelector().index(i)
                    .childSelector(new UiSelector().description(
                            String.valueOf(i + 1))));
            UiObject button = item.getFromParent(new UiSelector()
                    .descriptionMatches("下载 Link|继续 Link"));
            if (button.exists()) {
                button.click();
            }
        }

        // 点击管理
        UiObject manager = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/bottom_txt").text("管理"));
        manager.click();

        // 等待下载完成
        UiObject bubble = new UiObject(new UiSelector().resourceId(
                "com.qihoo.appstore:id/new_admin_new_bubble_download"));
        bubble.waitUntilGone(60 * 60 * 1000);
    }
}
