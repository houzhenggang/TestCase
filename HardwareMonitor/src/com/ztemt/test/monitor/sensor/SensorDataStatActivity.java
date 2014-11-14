package com.ztemt.test.monitor.sensor;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.os.Environment;
import android.text.TextUtils;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.ztemt.test.monitor.R;

public class SensorDataStatActivity extends Activity {

    private String mType;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.sensor_data_stat);

        String title = getIntent().getStringExtra("title");
        setTitle(title);

        mType = getIntent().getStringExtra("type");
        refresh(null);
    }

    public void refresh(View view) {
        File[] files = getDataFiles();
        if (files.length > 0) {
            LinearLayout container = (LinearLayout) findViewById(R.id.stat_item_container);
            container.removeAllViews();
            showDataStat(files);
        }
    }

    public void clear(View view) {
        File[] files = getDataFiles();
        for (File file : files) {
            file.delete();
        }
        finish();
    }

    private File[] getDataFiles() {
        File dir = new File(Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS), SensorUtilityFunctions.TAG);
        File[] files = dir.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String filename) {
                if (filename.startsWith(mType)) return true;
                return false;
            }
        });
        Arrays.sort(files, new Comparator<File>() {
            @Override
            public int compare(File lhs, File rhs) {
                return rhs.getName().compareTo(lhs.getName());
            }
        });
        return files;
    }

    private void showDataStat(File[] files) {
        if (files.length > 0) {
            addDataStat(files[0]);
        }
        if (files.length > 1) {
            addDataStat(files[1]);
        }
        if (files.length > 2) {
            addDataStat(files[2]);
        }
    }

    @SuppressLint("InflateParams")
    private void addDataStat(File file) {
        View v = getLayoutInflater().inflate(R.layout.sensor_data_stat_item, null, false);
        TextView title = (TextView) v.findViewById(R.id.stat_title);
        title.setText(file.getName());

        List<Float> xList = new ArrayList<Float>();
        List<Float> yList = new ArrayList<Float>();
        List<Float> zList = new ArrayList<Float>();

        try {
            BufferedReader br = new BufferedReader(new FileReader(file));
            String line = null;
            boolean start = false;
            while ((line = br.readLine()) != null) {
                if (line.toUpperCase(Locale.getDefault()).startsWith("X,Y,Z,ACCURACY,TIME")) {
                    start = true;
                } else if (TextUtils.isEmpty(line)) {
                    start = false;
                } else if (start) {
                    String ss[] = line.split(",");
                    xList.add(Float.parseFloat(ss[0]));
                    yList.add(Float.parseFloat(ss[1]));
                    zList.add(Float.parseFloat(ss[2]));
                }
            }
            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        double[] xxx = getStatData(xList.toArray(new Float[xList.size()]));
        TextView xMin = (TextView) v.findViewById(R.id.stat_x_min);
        xMin.setText(String.valueOf(xxx[0]));
        TextView xMax = (TextView) v.findViewById(R.id.stat_x_max);
        xMax.setText(String.valueOf(xxx[1]));
        TextView xAve = (TextView) v.findViewById(R.id.stat_x_ave);
        xAve.setText(String.valueOf(xxx[2]));
        TextView xVar = (TextView) v.findViewById(R.id.stat_x_var);
        xVar.setText(String.valueOf(xxx[3]));

        double[] yyy = getStatData(yList.toArray(new Float[yList.size()]));
        TextView yMin = (TextView) v.findViewById(R.id.stat_y_min);
        yMin.setText(String.valueOf(yyy[0]));
        TextView yMax = (TextView) v.findViewById(R.id.stat_y_max);
        yMax.setText(String.valueOf(yyy[1]));
        TextView yAve = (TextView) v.findViewById(R.id.stat_y_ave);
        yAve.setText(String.valueOf(yyy[2]));
        TextView yVar = (TextView) v.findViewById(R.id.stat_y_var);
        yVar.setText(String.valueOf(yyy[3]));

        double[] zzz = getStatData(zList.toArray(new Float[zList.size()]));
        TextView zMin = (TextView) v.findViewById(R.id.stat_z_min);
        zMin.setText(String.valueOf(zzz[0]));
        TextView zMax = (TextView) v.findViewById(R.id.stat_z_max);
        zMax.setText(String.valueOf(zzz[1]));
        TextView zAve = (TextView) v.findViewById(R.id.stat_z_ave);
        zAve.setText(String.valueOf(zzz[2]));
        TextView zVar = (TextView) v.findViewById(R.id.stat_z_var);
        zVar.setText(String.valueOf(zzz[3]));

        LinearLayout container = (LinearLayout) findViewById(R.id.stat_item_container);
        container.addView(v);
    }

    private double[] getStatData(Float[] array) {
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
}
