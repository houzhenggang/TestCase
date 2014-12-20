package com.ztemt.test.stress.item;

import android.content.Context;
import android.hardware.Sensor;

import com.ztemt.test.stress.R;

public class LightSensorTest extends SensorTest {

    public LightSensorTest(Context context) {
        super(context, Sensor.TYPE_LIGHT);
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.light_sensor_test);
    }
}
