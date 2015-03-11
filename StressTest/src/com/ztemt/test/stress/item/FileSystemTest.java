package com.ztemt.test.stress.item;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.math.BigInteger;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import android.content.Context;

import com.ztemt.test.stress.R;

public class FileSystemTest extends BaseTest {

    public FileSystemTest(Context context) {
        super(context);
    }

    @Override
    public void onRun() {
        File source = new File(mContext.getExternalFilesDir(""), "test");
        File target = new File("/data", "test");
        boolean success = false;

        if (copy(source, target)) {
            String str1 = getFileDigest(source);
            String str2 = getFileDigest(target);
            success = str1 != null && str2 != null && str1.equals(str2);
            target.delete();
        }

        if (success) {
            setSuccess();
        } else {
            setFailure();
        }
    }

    @Override
    public String getTitle() {
        return mContext.getString(R.string.file_system_test);
    }

    private boolean copy(File source, File target) {
        int length = 1024;
        int size;
        byte[] buffer = new byte[length];

        InputStream is = null;
        OutputStream os = null;

        try {
            is = new FileInputStream(source);
            os = new FileOutputStream(target);
            while ((size = is.read(buffer, 0, length)) != -1) {
                os.write(buffer, 0, size);
            }
            return true;
        } catch (Exception e) {
            return false;
        } finally {
            if (os != null) {
                try {
                    os.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            if (is != null) {
                try {
                    is.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    private String getFileDigest(File file) {
        try {
            return getFileDigest(new FileInputStream(file));
        } catch (FileNotFoundException e) {
            return null;
        }
    }

    private String getFileDigest(InputStream is) {
        byte[] buffer = new byte[1024];
        DigestInputStream dis = null;

        try {
            dis = new DigestInputStream(is, MessageDigest.getInstance("MD5"));
            while (dis.read(buffer) != -1) {
                /* Nothing to do! */
            }
            BigInteger bi = new BigInteger(1, dis.getMessageDigest().digest());
            return bi.toString(16);
        } catch (NoSuchAlgorithmException e) {
            return null;
        } catch (IOException e) {
            return null;
        } finally {
            if (dis != null) {
                try {
                    dis.close();
                    dis = null;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
