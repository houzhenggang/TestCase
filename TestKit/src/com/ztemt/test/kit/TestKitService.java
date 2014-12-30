package com.ztemt.test.kit;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.KeyguardManager;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.PackageManager.NameNotFoundException;
import android.content.pm.ResolveInfo;
import android.os.IBinder;
import android.os.RemoteException;

public class TestKitService extends Service {

    public static final String EXTRA_COMMAND = "command";
    public static final String ACTION_BINDER = "com.ztemt.test.action.TEST_KIT";

    private TestKit.Stub mBinder = new TestKit.Stub() {

        @Override
        public void notifyStop(byte[] bytes, String filename)
                throws RemoteException {
            write(bytes, getFileStreamPath(filename));
        }
    };

    @SuppressWarnings("deprecation")
    private KeyguardManager.KeyguardLock mKeyguardLock;

    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        getFilesDir().setReadable(true, false);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            String command = intent.getStringExtra(EXTRA_COMMAND);
            if ("getPackageList".equals(command)) {
                getPackageList();
            } else if ("disableKeyguard".equals(command)) {
                enableKeyguard(false);
            } else if ("enableKeyguard".equals(command)) {
                enableKeyguard(true);
            }
        }
        return START_NOT_STICKY;
    }

    private void getPackageList() {
        String[] categories = { Intent.CATEGORY_LAUNCHER, Intent.CATEGORY_HOME };
        JSONObject jobj = new JSONObject();

        for (String category : categories) {
            Intent query = new Intent(Intent.ACTION_MAIN).addCategory(category);
            List<ResolveInfo> activities = getPackageManager()
                    .queryIntentActivities(query, 0);
    
            for (ResolveInfo info : activities) {
                String packageName = info.activityInfo.packageName;
                JSONObject activity = new JSONObject();
    
                try {
                    activity.put("title", info.loadLabel(getPackageManager()).toString());
                    activity.put("name", info.activityInfo.name);
                    activity.put("category", category);
                    if (jobj.has(packageName)) {
                        jobj.optJSONObject(packageName).getJSONArray("activities")
                                .put(activity);
                    } else {
                        PackageInfo pkgInfo = getPackageManager().getPackageInfo(
                                packageName, PackageManager.GET_META_DATA);
                        JSONObject obj = new JSONObject();
                        obj.put("versionCode", pkgInfo.versionCode);
                        obj.put("versionName", pkgInfo.versionName);
                        obj.put("activities", new JSONArray().put(activity));
                        jobj.put(packageName, obj);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                } catch (NameNotFoundException e) {
                    e.printStackTrace();
                }
            }

            String[] others = { "com.android.systemui" };
            for (String packageName : others) {
                if (!jobj.has(packageName)) {
                    try {
                        PackageInfo pkgInfo = getPackageManager().getPackageInfo(
                                packageName, PackageManager.GET_META_DATA);
                        JSONObject obj = new JSONObject();
                        obj.put("versionCode", pkgInfo.versionCode);
                        obj.put("versionName", pkgInfo.versionName);
                        obj.put("activities", new JSONArray());
                        jobj.put(packageName, obj);
                    } catch (NameNotFoundException e) {
                        e.printStackTrace();
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }
            }
        }

        // Save package list to external storage
        File file = getFileStreamPath("packages");
        write(jobj.toString(), file);
    }

    private static void write(String line, File file) {
        BufferedWriter bw = null;
        try {
            FileWriter fw = new FileWriter(file, false);
            bw = new BufferedWriter(fw);
            bw.write(System.currentTimeMillis() + "\n");
            bw.write(line);
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (bw != null) {
                try {
                    bw.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        file.setReadable(true, false);
    }

    private static void write(byte[] bytes, File file) {
        FileOutputStream fos = null;
        try {
            fos = new FileOutputStream(file);
            fos.write((System.currentTimeMillis() + "\n").getBytes());
            fos.write(bytes);
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (fos != null) {
                try {
                    fos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        file.setReadable(true, false);
    }

    @SuppressWarnings("deprecation")
    private void enableKeyguard(boolean enabled) {
        if (mKeyguardLock == null) {
            KeyguardManager km = (KeyguardManager) getSystemService(KEYGUARD_SERVICE);
            mKeyguardLock = km.newKeyguardLock("keyguard");
        }
        if (enabled) {
            mKeyguardLock.reenableKeyguard();
        } else {
            mKeyguardLock.disableKeyguard();
        }
    }
}
