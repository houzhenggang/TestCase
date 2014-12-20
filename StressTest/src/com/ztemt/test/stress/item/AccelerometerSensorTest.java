package com.ztemt.test.stress.item;

import android.content.Context;
import android.hardware.Sensor;

import com.ztemt.test.stress.R;

public class AccelerometerSensorTest extends SensorTest {

    public AccelerometerSensorTest(Context context) {
        super(context, Sensor.TYPE_ACCELEROMETER);
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.accelerometer_sensor_test);
    }
}
