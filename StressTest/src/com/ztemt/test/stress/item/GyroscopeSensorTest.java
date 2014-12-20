package com.ztemt.test.stress.item;

import android.content.Context;
import android.hardware.Sensor;

import com.ztemt.test.stress.R;

public class GyroscopeSensorTest extends SensorTest {

    public GyroscopeSensorTest(Context context) {
        super(context, Sensor.TYPE_GYROSCOPE);
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.gyroscope_sensor_test);
    }
}
