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
    // Log writer
    private BufferedWriter mLogWriter;

    /**
     * @param text String to be written into the log file.
     * 
     * Log file name is determined by database property, and will be located
     * within the device's downloads folder.
     */
    private synchronized void writeToLogFile(String text) {
        try {
            if (mLogWriter != null) {
                mLogWriter.write(text);
                mLogWriter.flush();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void createLogWriter() {
        int logFileBufferSize = 100;

        File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS), SensorUtilityFunctions.TAG);
        dir.mkdir();

        File logFile = new File(dir, getSensorType() + "_" + System.currentTimeMillis() + ".csv");
        try {
            FileWriter fstream = new FileWriter(logFile, false);
            mLogWriter = new BufferedWriter(fstream, logFileBufferSize);
            mLogWriter.write("X,Y,Z,ACCURACY,TIMESTAMP\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void closeLogWriter() {
        try {
            if (mLogWriter != null) {
                mLogWriter.close();
                mLogWriter = null;
            }
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

        writeToLogFile(data0 + "," + data1 + "," + data2 + "," + accuracy + "," + timestamp + "\n");
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
