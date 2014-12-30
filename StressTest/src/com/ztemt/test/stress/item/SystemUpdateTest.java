package com.ztemt.test.stress.item;

import java.io.File;
import java.io.IOException;

import android.content.Context;
import android.os.Environment;
import android.os.RecoverySystem;
import android.util.Log;

import com.ztemt.test.stress.R;

public class SystemUpdateTest extends BaseTest {

    private static final String LOG_TAG = "SystemUpdateTest";

    public SystemUpdateTest(Context context) {
        super(context);
    }

    @Override
    public void onRun() {
        File file = new File(Environment.getExternalStorageDirectory(), "update.zip");
        if (file.exists()) {
            try {
                setSuccess();
                RecoverySystem.installPackage(mContext, file);
                pause();
            } catch (IOException e) {
                Log.e(LOG_TAG, e.getMessage());
            }
        }
        Log.w(LOG_TAG, "Fail to install package " + file.getPath());
        setFailure();
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.system_update_test);
    }
}
