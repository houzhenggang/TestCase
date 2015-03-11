package com.ztemt.test.kit;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.KeyguardManager;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Environment;
import android.os.FileObserver;
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

    private Set<String> mObserverDirs = new HashSet<String>();

    private RecursiveFileObserver mObserver = new RecursiveFileObserver(
            Environment.getExternalStorageDirectory().getAbsolutePath()) {

        @Override
        public void onEvent(int event, String path) {
            switch (event) {
            case FileObserver.DELETE:
                mObserverDirs.add(new File(path).getParent());
                break;
            default:
                super.onEvent(event, path);
                break;
            }
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
            } else if ("startWatching".equals(command)) {
                startWatching();
            } else if ("stopWatching".equals(command)) {
                stopWatching();
            }
        }
        return START_NOT_STICKY;
    }

    private void getPackageList() {
        String[] categories = { Intent.CATEGORY_LAUNCHER, Intent.CATEGORY_HOME };
        PackageManager pm = getPackageManager();
        JSONObject jobj = new JSONObject();

        for (PackageInfo pi : pm.getInstalledPackages(0)) {
            String packageName = pi.packageName;

            JSONObject obj = new JSONObject();
            try {
                obj.put("versionCode", pi.versionCode);
                obj.put("versionName", pi.versionName);
                obj.put("activities", new JSONArray());
                jobj.put(packageName, obj);
            } catch (JSONException e) {
                e.printStackTrace();
            }

            for (String category : categories) {
                Intent intent = new Intent(Intent.ACTION_MAIN).addCategory(
                        category).setPackage(packageName);
                List<ResolveInfo> activities = pm.queryIntentActivities(intent, 0);

                for (ResolveInfo ri : activities) {
                    JSONObject activity = new JSONObject();
                    try {
                        activity.put("title", ri.loadLabel(pm).toString());
                        activity.put("name", ri.activityInfo.name);
                        activity.put("category", category);
                        if (jobj.has(packageName)) {
                            jobj.optJSONObject(packageName).getJSONArray(
                                    "activities").put(activity);
                        }
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

    private static void write(String[] lines, File file) {
        BufferedWriter bw = null;
        try {
            FileWriter fw = new FileWriter(file, false);
            bw = new BufferedWriter(fw);
            bw.write(System.currentTimeMillis() + "\n");
            for (int i = 0; i < lines.length; i++) {
                if (i == 0) {
                    bw.write(lines[i]);
                } else {
                    bw.write("\n" + lines[i]);
                }
            }
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

    private static void write(String line, File file) {
        write(new String[] { line }, file);
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

    private void startWatching() {
        mObserver.startWatching();
    }

    private void stopWatching() {
        mObserver.stopWatching();
        String[] dirs = mObserverDirs.toArray(new String[mObserverDirs.size()]);
        write(dirs, getFileStreamPath("observer"));
        mObserverDirs.clear();
    }
}
