package com.a1dev.sdbench;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

import android.text.TextUtils;
import android.widget.ListView;
import android.widget.ProgressBar;

import com.android.uiautomator.core.UiObject;
import com.android.uiautomator.core.UiObjectNotFoundException;
import com.android.uiautomator.core.UiScrollable;
import com.android.uiautomator.core.UiSelector;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;

public class A1SDBenchTestCase extends UiAutomatorTestCase {

    private static final String BENCHMARK = "/data/local/tmp/a1sdbenchmark";

    @Override
    protected void setUp() throws Exception {
        super.setUp();

        String cmd = "am start -n com.a1dev.sdbench/.A1SDBenchStart";
        Process p = Runtime.getRuntime().exec(cmd);
        p.waitFor();

        sleep(3000);

        getUiDevice().setOrientationNatural();
    }

    public void testBenchmark() throws UiObjectNotFoundException, IOException {
        UiObject benchmark = new UiObject(new UiSelector().text("Benchmark"));
        benchmark.click();

        UiScrollable list = new UiScrollable(new UiSelector().className(ListView.class));
        BufferedWriter bw = new BufferedWriter(new FileWriter(BENCHMARK));
        for (int i = 0; i < list.getChildCount(); i++) {
            UiObject storage = list.getChild(new UiSelector().index(i).childSelector(
                    new UiSelector().index(1).childSelector(
                    new UiSelector().index(0))));
            if (storage.exists()) {
                UiObject result = storage.getFromParent(new UiSelector().index(2));
                if (result.exists() && !TextUtils.isEmpty(result.getText())) {
                    storage.click();
                    UiObject progress = new UiObject(new UiSelector().className(
                            ProgressBar.class));
                    assertTrue(progress.waitUntilGone(10 * 60 * 1000));
                    if (!TextUtils.isEmpty(result.getText())) {
                        bw.write(String.format("%s,%s\n", storage.getText(),
                                result.getText()));
                        bw.flush();
                    }
                }
            }
        }
        bw.close();
    }
}
