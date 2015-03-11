package com.tencent.mobileqq;

import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiSelector;
import com.ztemt.test.automator.AutomatorTestCase;

public class MobileQQTestCase extends AutomatorTestCase {

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start --activity-clear-task -n com.tencent.mobileqq/.activity.SplashActivity";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();
    }

    public void testLogin() throws UiObjectNotFoundException {
        UiObject validation = new UiObject(new UiSelector().packageName(
                "com.tencent.mobileqq"));
        assertTrue(validation.waitForExists(5000));

        UiObject remember = new UiObject(new UiSelector().className(
                CheckBox.class).text("不再提醒"));
        if (remember.exists()) {
            remember.click();
            UiObject gotonext = new UiObject(new UiSelector().className(
                    Button.class).text("继续"));
            gotonext.click();

            UiObject progress = new UiObject(new UiSelector().className(
                    ProgressBar.class));
            progress.waitUntilGone(30000);

            getUiDevice().pressBack();
        }

        UiObject login = new UiObject(new UiSelector().resourceId(
                "com.tencent.mobileqq:id/btn_login"));
        if (login.exists()) {
            login.click();
        }
        UiObject username = new UiObject(new UiSelector().resourceId(
                "com.tencent.mobileqq:id/input").childSelector(new UiSelector()
                .className(RelativeLayout.class).childSelector(new UiSelector()
                .className(EditText.class))));
        if (username.exists()) {
            username.click();
            UiObject cleartxt = new UiObject(new UiSelector().resourceId(
                    "com.tencent.mobileqq:id/input").childSelector(new UiSelector()
                    .className(RelativeLayout.class).childSelector(new UiSelector()
                    .className(LinearLayout.class).childSelector(new UiSelector()
                    .className(ImageView.class)))));
            if (cleartxt.exists()) {
                cleartxt.click();
            }
            username.setText("1330737871");
            UiObject password = new UiObject(new UiSelector().resourceId(
                    "com.tencent.mobileqq:id/password"));
            password.click();
            password.clickBottomRight();
            password.setText("ztemt123");
            UiObject loginbtn = new UiObject(new UiSelector().resourceId(
                    "com.tencent.mobileqq:id/login"));
            loginbtn.clickAndWaitForNewWindow();
        }
    }
}
