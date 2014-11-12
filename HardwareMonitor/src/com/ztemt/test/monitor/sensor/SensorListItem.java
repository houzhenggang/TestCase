package com.ztemt.test.monitor.sensor;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

import android.hardware.Sensor;
import android.os.Environment;
import android.util.Log;

public class SensorListItem {

    static private final String TAG = "SensorListItem";
    static private List<SensorListItem> sSensorList;
    static private int sEffectiveRateCount;

    static {
        sSensorList = new ArrayList<SensorListItem>();
        sEffectiveRateCount = 5;
    }

    static public List<SensorListItem> createSensorList(List<Sensor> sensorList) {
        List<SensorListItem> sensorItemList = new ArrayList<SensorListItem>(
                sensorList.size());
        for (Sensor sensor : sensorList) {
            if (SensorUtilityFunctions.isPhysicalSensor(sensor)) {
                SensorListItem sensorItem = new SensorListItem(sensor);
                sensorItemList.add(sensorItem);
            }
        }
        sSensorList = sensorItemList;
        return sensorItemList;
    }

    static public List<SensorListItem> getSensorList() {
        return sSensorList;
    }

    // Sensor we are wrapping around
    private Sensor mSensor;
    // Data from the most recent update
    private float[] mData;
    // Timestamp of the last update
    private long mTimestamp;
    // Current stream rate (as set by the user)
    private int mStreamRate;
    // Accuracy of the data as reported by the sensor
    private int mAccuracy;
    // When the past several updates were received
    private LinkedList<Date> mRcvTimes;

    private List<Float> mData0List = new ArrayList<Float>();
    private List<Float> mData1List = new ArrayList<Float>();
    private List<Float> mData2List = new ArrayList<Float>();
    private List<Integer> mAccuracyList = new ArrayList<Integer>();
    private List<Long> mTimestampList = new ArrayList<Long>();

    private double[] statData(Float[] array) {
        if (array == null || array.length == 0) {
            return new double[] { 0, 0, 0, 0 };
        } else {
            double sum = 0, min = array[0], max = array[0], ave;
    
            for (int i = 0; i < array.length; i++) {
                if (array[i] < min) {
                    min = array[i];
                } else if (array[i] > max) {
                    max = array[i];
                }
                sum += array[i];
            }
            ave = sum / array.length;

            double varsum = 0, var;
            for (int i = 0; i < array.length; i++) {
                varsum += (array[i] - ave) * (array[i] - ave);
            }
            var = varsum / array.length;

            return new double[] { min, max, ave, var };
        }
    }

    public void createDataReport() {
        File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS), SensorUtilityFunctions.TAG);
        dir.mkdir();

        File logFile = new File(dir, getSensorType() + "_" + System.currentTimeMillis() + ".csv");
        try {
            FileWriter fstream = new FileWriter(logFile, false);
            BufferedWriter logWriter = new BufferedWriter(fstream, 100);
            logWriter.write("X,Y,Z,ACCURACY,TIMESTAMP\n");
            for (int i = 0; i < mData0List.size(); i++) {
                logWriter.write(mData0List.get(i) + "," + mData1List.get(i) + ","
                        + mData2List.get(i) + "," + mAccuracyList.get(i) + ","
                        + mTimestampList.get(i) + "\n");
            }
            logWriter.newLine();
            logWriter.write(",Min.,Max.,Ave.,Var.\n");
            double[] xxx = statData(mData0List.toArray(new Float[mData0List.size()]));
            logWriter.write("X," + xxx[0] + "," + xxx[1] + "," + xxx[2] + "," + xxx[3] + "\n");
            double[] yyy = statData(mData1List.toArray(new Float[mData1List.size()]));
            logWriter.write("Y," + yyy[0] + "," + yyy[1] + "," + yyy[2] + "," + yyy[3] + "\n");
            double[] zzz = statData(mData2List.toArray(new Float[mData2List.size()]));
            logWriter.write("Z," + zzz[0] + "," + zzz[1] + "," + zzz[2] + "," + zzz[3] + "\n");
            logWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public SensorListItem(Sensor sensor) {
        mSensor = sensor;
        mStreamRate = -1;
        mAccuracy = 0;
        mTimestamp = 0;
        mData = new float[3];
        mData[0] = 0;
        mData[1] = 0;
        mData[2] = 0;
        mRcvTimes = new LinkedList<Date>();
    }

    public Sensor getSensor() {
        return mSensor;
    }

    public int getAccuracy() {
        return mAccuracy;
    }

    public float[] getData() {
        return mData;
    }

    public long getTimestamp() {
        return mTimestamp;
    }

    public String getSensorName() {
        return mSensor.getName();
    }

    public String getSensorType() {
        return SensorUtilityFunctions.getSensorTypeString(mSensor);
    }

    public String getSensorUnit() {
        return SensorUtilityFunctions.getSensorUnitString(mSensor);
    }

    public double getSensorChartMaxX() {
        return SensorUtilityFunctions.getSensorChartMaxX(mSensor);
    }

    public double getSensorChartMinY() {
        return SensorUtilityFunctions.getSensorChartMinY(mSensor);
    }

    public double getSensorChartMaxY() {
        return SensorUtilityFunctions.getSensorChartMaxY(mSensor);
    }

    public int getStreamRate() {
        return mStreamRate;
    }

    public LinkedList<Date> getRcvTimes() {
        return mRcvTimes;
    }

    public void setAccuracy(int accuracy) {
        mAccuracy = accuracy;
    }

    public void setData(float data0, float data1, float data2, int accuracy,
            long timestamp) {
        mData[0] = data0;
        mData[1] = data1;
        mData[2] = data2;

        if (mTimestamp > timestamp) {
            Log.e(TAG, "Log misorder: " + getSensorType() + " (" + mTimestamp
                    + "," + timestamp + ")");
        }

        mTimestamp = timestamp;
        mAccuracy = accuracy;

        mRcvTimes.addFirst(new Date());
        if (mRcvTimes.size() > sEffectiveRateCount) {
            mRcvTimes.removeLast();
        }

        mData0List.add(data0);
        mData1List.add(data1);
        mData2List.add(data2);
        mAccuracyList.add(accuracy);
        mTimestampList.add(timestamp);
    }

    public void setStreamRate(int streamRate) {
        mStreamRate = streamRate;

        if (streamRate == 0) {
            mRcvTimes.clear();
        }
    }

    /**
     * @return The title of the sensor with form "SensorType: SensorName" or "SensorType: Vendor"
     */
    public String getTitle() {
        // Test team request: For virtual sensors, display title as "SensorType: Vendor"
        if (mSensor.getType() == Sensor.TYPE_GRAVITY ||
                mSensor.getType() == Sensor.TYPE_LINEAR_ACCELERATION ||
                mSensor.getType() == Sensor.TYPE_ROTATION_VECTOR) {
            return getSensorType() + ": " + mSensor.getVendor();
        } else {
            return getSensorType() + ": " + getSensorName();
        }
    }
}
