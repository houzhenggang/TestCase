package com.ztemt.test.stress.item;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import com.ztemt.test.stress.R;

public class PowerOnOffTest extends BaseTest {

    private static final String LOG_TAG = "PowerOnOffTest";

    public PowerOnOffTest(Context context) {
        super(context);
    }

    @Override
    public void onRun() {
        sleep(60 * 1000);

        // Set alarm power on
        long time = System.currentTimeMillis() + 360 * 1000;
        Intent intent = new Intent(Intent.ACTION_BOOT_COMPLETED);
        intent.putExtra("seq", 1);
        PendingIntent pi = PendingIntent.getBroadcast(mContext, 0, intent,
                PendingIntent.FLAG_CANCEL_CURRENT);
        AlarmManager alarmManager = (AlarmManager) mContext.getSystemService(
                Context.ALARM_SERVICE);
        alarmManager.set(4, time, pi);

        // Shutdown
        Log.d(LOG_TAG, "Performing shutdown...");
        Intent shutdown = new Intent("android.intent.action.ACTION_REQUEST_SHUTDOWN");
        shutdown.putExtra("android.intent.extra.KEY_CONFIRM", false);
        shutdown.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        mContext.startActivity(shutdown);

        setSuccess();
        pause();
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.power_on_off_test);
    }
}
