package com.wasteland.recruit;

import android.Manifest;
import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;

import java.io.OutputStream;

/** Hosts the generator page in a WebView and lets it save/share the rendered sheet. */
public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(22, 24, 29));
        getWindow().setNavigationBarColor(Color.rgb(22, 24, 29));
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(22, 24, 29));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setAllowFileAccess(true);
        s.setDomStorageEnabled(true);
        s.setBuiltInZoomControls(false);
        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        setContentView(web);
        if (state != null) web.restoreState(state);
        else web.loadUrl("file:///android_asset/www/index.html");
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    private static byte[] decode(String dataUrl) {
        int comma = dataUrl.indexOf(',');
        return Base64.decode(comma >= 0 ? dataUrl.substring(comma + 1) : dataUrl, Base64.DEFAULT);
    }

    /** Writes the PNG into Pictures/Fallout Characters and returns its content URI (or null). */
    private Uri store(byte[] png, String name) throws Exception {
        ContentResolver cr = getContentResolver();
        if (Build.VERSION.SDK_INT >= 29) {
            ContentValues v = new ContentValues();
            v.put(MediaStore.Images.Media.DISPLAY_NAME, name);
            v.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
            v.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/Fallout Characters");
            v.put(MediaStore.Images.Media.IS_PENDING, 1);
            Uri uri = cr.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, v);
            if (uri == null) return null;
            try (OutputStream os = cr.openOutputStream(uri)) {
                os.write(png);
            }
            v.clear();
            v.put(MediaStore.Images.Media.IS_PENDING, 0);
            cr.update(uri, v, null, null);
            return uri;
        }
        if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 1));
            throw new IllegalStateException("allow storage access, then tap again");
        }
        Bitmap bmp = BitmapFactory.decodeByteArray(png, 0, png.length);
        String s = MediaStore.Images.Media.insertImage(cr, bmp, name, "Fallout character sheet");
        return s == null ? null : Uri.parse(s);
    }

    class Bridge {
        @JavascriptInterface
        public String saveImage(String dataUrl, String name) {
            try {
                Uri uri = store(decode(dataUrl), name);
                return uri == null ? "ERROR: could not save" : uri.toString();
            } catch (Exception e) {
                return "ERROR: " + e.getMessage();
            }
        }

        @JavascriptInterface
        public String shareImage(String dataUrl, String name, String title) {
            try {
                Uri uri = store(decode(dataUrl), name);
                if (uri == null) return "ERROR: could not prepare image";
                Intent send = new Intent(Intent.ACTION_SEND);
                send.setType("image/png");
                send.putExtra(Intent.EXTRA_STREAM, uri);
                send.putExtra(Intent.EXTRA_TEXT, title + " - Fallout 2d20 character");
                send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                Intent chooser = Intent.createChooser(send, "Share character sheet");
                runOnUiThread(() -> startActivity(chooser));
                return "OK";
            } catch (Exception e) {
                return "ERROR: " + e.getMessage();
            }
        }
    }
}
