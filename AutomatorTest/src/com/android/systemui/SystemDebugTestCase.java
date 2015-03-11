package com.android.systemui;

import java.io.IOException;

import android.os.Debug;

import com.ztemt.test.automator.AutomatorTestCase;

public class SystemDebugTestCase extends AutomatorTestCase {

    public void testDumpHprof() throws IOException {
        String fileName = getParams().getString("filename");
        Debug.dumpHprofData(fileName);
    }
}
