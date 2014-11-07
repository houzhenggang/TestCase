package com.ztemt.test.monitor.chart;

import org.achartengine.ChartFactory;
import org.achartengine.chart.PointStyle;
import org.achartengine.model.XYMultipleSeriesDataset;
import org.achartengine.model.XYSeries;
import org.achartengine.renderer.XYMultipleSeriesRenderer;
import org.achartengine.renderer.XYSeriesRenderer;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Paint.Align;
import android.os.SystemClock;
import android.view.View;

public class AxisLineChart extends AbstractChart {

    private Context mContext;
    private XYMultipleSeriesDataset mDataset;
    private View mView;

    private long mTimestamp = SystemClock.elapsedRealtime();
    private int mSeriesCount;
    private double mMaxX;

    public AxisLineChart(Context context, String title, String unit, double maxX,
            double minY, double maxY, int seriesCount) {
        mContext = context;
        mSeriesCount = seriesCount;
        mMaxX = maxX;

        if (mSeriesCount == 1) {
            mDataset = buildDataset(new String[] { "[0]" });
        } else if (mSeriesCount == 2) {
            mDataset = buildDataset(new String[] { "[0]", "[1]" });
        } else {
            mDataset = buildDataset(new String[] { "[0]", "[1]", "[2]" });
        }

        mView = createView(title, unit, minY, maxY);
    }

    private View createView(String title, String unit, double minY, double maxY) {
        PointStyle[] styles;
        int[] colors;

        if (mSeriesCount == 1) {
            colors = new int[] { Color.RED };
            styles = new PointStyle[] { PointStyle.POINT };
        } else if (mSeriesCount == 2) {
            colors = new int[] { Color.RED, Color.GREEN };
            styles = new PointStyle[] { PointStyle.POINT, PointStyle.POINT };
        } else {
            colors = new int[] { Color.RED, Color.GREEN, Color.BLUE };
            styles = new PointStyle[] { PointStyle.POINT, PointStyle.POINT,
                    PointStyle.POINT };
        }

        XYMultipleSeriesRenderer renderer = buildRenderer(colors, styles);
        for (int i = 0; i < renderer.getSeriesRendererCount(); i++) {
            ((XYSeriesRenderer) renderer.getSeriesRendererAt(i))
                    .setFillPoints(true);
        }
        setChartSettings(renderer, title, "Time", unit, 0, mMaxX, minY,
                maxY, Color.LTGRAY, Color.LTGRAY);
        renderer.setXLabels(12);
        renderer.setYLabels(10);
        renderer.setShowGrid(true);
        renderer.setXLabelsAlign(Align.RIGHT);
        renderer.setYLabelsAlign(Align.RIGHT);
        renderer.setZoomButtonsVisible(true);
        return ChartFactory.getLineChartView(mContext, mDataset, renderer);
    }

    public View getView() {
        return mView;
    }

    public void update(final double[] values) {
        for (int i = 0; i < mDataset.getSeriesCount(); i++) {
            XYSeries series = mDataset.getSeriesAt(i);
            int length = series.getItemCount();
            if (length > mMaxX) {
                series.clear();
                length = 0;
            }
            if (length == 0) {
                series.add(0, values[i]);
            } else {
                series.add(series.getX(length - 1) + 1, values[i]);
            }
        }

        // Update view
        if (SystemClock.elapsedRealtime() - mTimestamp > 200) {
            mView.invalidate();
            mTimestamp = SystemClock.elapsedRealtime();
        }
    }
}
