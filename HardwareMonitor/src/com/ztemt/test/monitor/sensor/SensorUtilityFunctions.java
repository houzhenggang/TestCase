package com.ztemt.test.monitor.sensor;

import java.util.Date;
import java.util.LinkedList;

import android.hardware.Sensor;
import android.hardware.SensorManager;

final public class SensorUtilityFunctions {

    static final String TAG = "Sensor";

    /**
     * @return A string representing what the current stream rate means in the Android framework
     */
    static public String streamRateString(int streamRate) {
        switch (streamRate) {
        case -1:
            return "Off";
        case SensorManager.SENSOR_DELAY_FASTEST:
            return "Fastest";
        case SensorManager.SENSOR_DELAY_GAME:
            return "Game";
        case SensorManager.SENSOR_DELAY_NORMAL:
            return "Normal";
        case SensorManager.SENSOR_DELAY_UI:
            return "UI";
        default:
            return String.valueOf(streamRate);
        }
    }

    static public double effectiveStreamRate(SensorListItem listItem) {
        LinkedList<Date> rcvTimes = listItem.getRcvTimes();
        if (rcvTimes.size() == 0 || rcvTimes.size() == 1) {
            return 0.0;
        } else {
            return 1000 / ((double) (rcvTimes.getFirst().getTime() - rcvTimes
                    .getLast().getTime()) / (rcvTimes.size() - 1));
        }
    }

    /**
     * @return A string containing the contents of the last update.
     */
    static public String getDataString(SensorListItem listItem) {
        String output = 
            "[0]:" + Float.toString(listItem.getData()[0]) + "\n" +
            "[1]:" + Float.toString(listItem.getData()[1]) + "\n" +
            "[2]:" + Float.toString(listItem.getData()[2]) + "\n" +
            "accuracy:" + getSensorAccuracyString(listItem.getAccuracy()) + "("
                    + Integer.toString(listItem.getAccuracy()) + ")\n" +
            "ts:" + Long.toString(listItem.getTimestamp());
        return output;
    }

    /**
     * Returns String value for the rate value
     * 
     * @param rate The sensor rate
     * @return String value for the rate
     */
    static private String getSensorAccuracyString(int rate) {
        String sensorAccuracyString;
        switch (rate) {
        case SensorManager.SENSOR_STATUS_UNRELIABLE:
            sensorAccuracyString = "UNRE";
            break;
        case SensorManager.SENSOR_STATUS_ACCURACY_LOW:
            sensorAccuracyString = "LOW ";
            break;
        case SensorManager.SENSOR_STATUS_ACCURACY_MEDIUM:
            sensorAccuracyString = "MEDI";
            break;
        case SensorManager.SENSOR_STATUS_ACCURACY_HIGH:
            sensorAccuracyString = "HIGH";
            break;
        default:
            sensorAccuracyString = "UNKN";
            break;
        }
        return sensorAccuracyString;
    }
    
    /**
     * Returns String value for the sensor type
     * 
     * @param sensor the sensor type 
     * @return String value for the sensor type
     */
    @SuppressWarnings("deprecation")
    static public String getSensorTypeString(Sensor sensor) {
        String sensorTypeString;
        switch (sensor.getType()) {
        case Sensor.TYPE_ACCELEROMETER:
            sensorTypeString = "ACCEL";
            break;
        case Sensor.TYPE_GYROSCOPE:
            sensorTypeString = "GYRO";
            break;
        case Sensor.TYPE_LIGHT:
            sensorTypeString = "LIGHT";
            break;
        case Sensor.TYPE_MAGNETIC_FIELD:
            sensorTypeString = "MAG";
            break;
        case Sensor.TYPE_ORIENTATION:
            sensorTypeString = "ORI";
            break;
        case Sensor.TYPE_PRESSURE:
            sensorTypeString = "PRESS";
            break;
        case Sensor.TYPE_PROXIMITY:
            sensorTypeString = "PROX";
            break;
        case Sensor.TYPE_TEMPERATURE:
            sensorTypeString = "TEMP";
            break;
        case Sensor.TYPE_LINEAR_ACCELERATION:
            sensorTypeString = "L.ACCEL";
            break;
        case Sensor.TYPE_GRAVITY:
            sensorTypeString = "GRAVITY";
            break;
        case Sensor.TYPE_ROTATION_VECTOR:
            sensorTypeString = "ROT VEC";
            break;
        default:
            //sensorTypeString = "UNKNOWN";
            sensorTypeString = sensor.getName();
            break;
        }

        return sensorTypeString;
    }

    /**
     *  Return string value for the sensor unit
     *  
     * @param sensor the sensor type
     * @return String value for the sensor unit
     */
    @SuppressWarnings("deprecation")
    static public String getSensorUnitString(Sensor sensor) {
        String sensorUnitString;
        switch (sensor.getType()) {
        case Sensor.TYPE_ACCELEROMETER:
            sensorUnitString = "Acceleration(m/sec^2)";
            break;
        case Sensor.TYPE_GYROSCOPE:
            sensorUnitString = "Angular Velocity(rad/sec)";
            break;
        case Sensor.TYPE_LIGHT:
            sensorUnitString = "Brightness(SI lux)";
            break;
        case Sensor.TYPE_MAGNETIC_FIELD:
            sensorUnitString = "Magnetic-field(uT)";
            break;
        case Sensor.TYPE_ORIENTATION:
            sensorUnitString = "Angle(°)";
            break;
        case Sensor.TYPE_PRESSURE:
            sensorUnitString = "Pressure(hPa)";
            break;
        case Sensor.TYPE_PROXIMITY:
            sensorUnitString = "Distance(cm)";
            break;
        case Sensor.TYPE_TEMPERATURE:
            sensorUnitString = "Temperature(℃)";
            break;
        case Sensor.TYPE_LINEAR_ACCELERATION:
            sensorUnitString = "Linear-Acceleration(m/sec^2)";
            break;
        case Sensor.TYPE_GRAVITY:
            sensorUnitString = "Gravity(m/sec^2)";
            break;
        case Sensor.TYPE_ROTATION_VECTOR:
            sensorUnitString = "Rotation Vector";
            break;
        default:
            sensorUnitString = sensor.getName();
            break;
        }

        return sensorUnitString;
    }

    @SuppressWarnings("deprecation")
    static public double getSensorChartMaxX(Sensor sensor) {
        double xMax;
        switch (sensor.getType()) {
        case Sensor.TYPE_LIGHT:
        case Sensor.TYPE_PRESSURE:
        case Sensor.TYPE_PROXIMITY:
        case Sensor.TYPE_TEMPERATURE:
            xMax = 50;
            break;
        default:
            xMax = 2000;
            break;
        }

        return xMax;
    }

    @SuppressWarnings("deprecation")
    static public double getSensorChartMinY(Sensor sensor) {
        double yMin;
        switch (sensor.getType()) {
        case Sensor.TYPE_ACCELEROMETER:
            yMin = -20.0;
            break;
        case Sensor.TYPE_GYROSCOPE:
            yMin = -40.0;
            break;
        case Sensor.TYPE_MAGNETIC_FIELD:
            yMin = -30.0;
            break;
        case Sensor.TYPE_ORIENTATION:
            yMin = -50.0;
            break;
        case Sensor.TYPE_TEMPERATURE:
            yMin = -40.0;
            break;
        case Sensor.TYPE_LINEAR_ACCELERATION:
            yMin = -30.0;
            break;
        case Sensor.TYPE_GRAVITY:
            yMin = -10.0;
            break;
        case Sensor.TYPE_ROTATION_VECTOR:
            yMin = -5.0;
            break;
        default:
            yMin = 0.0;
            break;
        }

        return yMin;
    }

    @SuppressWarnings("deprecation")
    static public double getSensorChartMaxY(Sensor sensor) {
        double yMax;
        switch (sensor.getType()) {
        case Sensor.TYPE_ACCELEROMETER:
            yMax = 20.0;
            break;
        case Sensor.TYPE_GYROSCOPE:
            yMax = 40.0;
            break;
        case Sensor.TYPE_LIGHT:
            yMax = 240.0;
            break;
        case Sensor.TYPE_MAGNETIC_FIELD:
            yMax = 30.0;
            break;
        case Sensor.TYPE_ORIENTATION:
            yMax = 150.0;
            break;
        case Sensor.TYPE_PROXIMITY:
            yMax = 15.0;
            break;
        case Sensor.TYPE_TEMPERATURE:
            yMax = 40.0;
            break;
        case Sensor.TYPE_LINEAR_ACCELERATION:
            yMax = 30.0;
            break;
        case Sensor.TYPE_GRAVITY:
            yMax = 10.0;
            break;
        case Sensor.TYPE_ROTATION_VECTOR:
            yMax = 5.0;
            break;
        default:
            yMax = 50.0;
            break;
        }

        return yMax;
    }

    @SuppressWarnings("deprecation")
    static public boolean isPhysicalSensor(Sensor sensor) {
        switch (sensor.getType()) {
        case Sensor.TYPE_ACCELEROMETER:
        case Sensor.TYPE_MAGNETIC_FIELD:
        case Sensor.TYPE_GYROSCOPE:
        case Sensor.TYPE_LIGHT:
        case Sensor.TYPE_PRESSURE:
        case Sensor.TYPE_TEMPERATURE:
        case Sensor.TYPE_PROXIMITY:
        case 9836800: // TYPE_VOLLEY_GESTURE
        case 9836801: // TYPE_HALL_DEVICE
            return true;
        default:
            return false;
        }
    }
}
