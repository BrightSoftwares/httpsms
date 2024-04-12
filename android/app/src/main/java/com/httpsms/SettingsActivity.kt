package com.httpsms

import android.Manifest
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Build.VERSION_CODES
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.widget.doAfterTextChanged
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import timber.log.Timber

class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        fillSettings(this)
        registerListeners()
    }

    private fun fillSettings(context: Context) {
        val debugLogs = findViewById<SwitchMaterial>(R.id.settingEnableDebugLogs)
        debugLogs.isChecked = Settings.isDebugLogEnabled(context)
        debugLogs.setOnCheckedChangeListener{ _, isChecked -> run { Settings.setDebugLogEnabled(context, isChecked) } }


        val phoneNumber = findViewById<TextInputEditText>(R.id.settingsSIM1Input)
        phoneNumber.setText(Settings.getSIM1PhoneNumber(context))
        phoneNumber.isEnabled = false

        val sim1IncomingMessages = findViewById<SwitchMaterial>(R.id.settings_sim1_incoming_messages)
        sim1IncomingMessages.isChecked = Settings.isIncomingMessageEnabled(context, Constants.SIM1)

        sim1IncomingMessages.setOnCheckedChangeListener{ _, isChecked -> run { Settings.setIncomingActiveSIM1(context, isChecked) } }

        val sim1OutgoingMessages = findViewById<SwitchMaterial>(R.id.settings_sim1_outgoing_messages)
        sim1OutgoingMessages.isChecked = Settings.getActiveStatus(context, Constants.SIM1)
        sim1OutgoingMessages.setOnCheckedChangeListener{ _, isChecked -> run { Settings.setActiveStatusAsync(context, isChecked, Constants.SIM1) } }

        if (!Settings.isDualSIM(context)) {
            val layout = findViewById<TextInputLayout>(R.id.settingsSIM2Layout)
            layout.visibility = TextInputLayout.GONE
            val sim2Switch = findViewById<SwitchMaterial>(R.id.settings_sim2_incoming_messages)
            sim2Switch.visibility = SwitchMaterial.GONE
            val outgoingSwitch = findViewById<SwitchMaterial>(R.id.settings_sim2_outgoing_messages)
            outgoingSwitch.visibility = SwitchMaterial.GONE
            return
        }

        val phoneNumberSIM2 = findViewById<TextInputEditText>(R.id.settingsSIM2InputEdit)
        phoneNumberSIM2.setText(Settings.getSIM2PhoneNumber(context))
        phoneNumberSIM2.isEnabled = false

        val sim2IncomingMessages = findViewById<SwitchMaterial>(R.id.settings_sim2_incoming_messages)
        sim2IncomingMessages.isChecked = Settings.isIncomingMessageEnabled(context, Constants.SIM2)
        sim2IncomingMessages.setOnCheckedChangeListener{ _, isChecked -> run { Settings.setIncomingActiveSIM2(context, isChecked) } }

        val sim2OutgoingMessages = findViewById<SwitchMaterial>(R.id.settings_sim2_outgoing_messages)
        sim2OutgoingMessages.isChecked = Settings.getActiveStatus(context, Constants.SIM2)
        sim2OutgoingMessages.setOnCheckedChangeListener{ _, isChecked -> run { Settings.setActiveStatusAsync(context, isChecked, Constants.SIM2) } }

        handleEncryptionSettings(context)
        handleIncomingCallEventsSim1(context)
    }

    private fun handleIncomingCallEventsSim1(context: Context) {
        val enableIncomingCallEvents = findViewById<SwitchMaterial>(R.id.settingsSim1EnableIncomingCallEvents)
        enableIncomingCallEvents.isChecked = Settings.isIncomingCallEventsEnabled(context, Constants.SIM1)
        enableIncomingCallEvents.setOnCheckedChangeListener{ _, isChecked -> run {
            requestReadCallLogPermission(context)
            Timber.d("how are you [${isChecked}]")
        }}
    }

    private fun handleEncryptionSettings(context: Context) {
        val encryptionKey = findViewById<TextInputEditText>(R.id.settingsEncryptionKeyInputEdit)
        val encryptReceivedMessages = findViewById<SwitchMaterial>(R.id.settingsEncryptReceivedMessages)

        val key = Settings.getEncryptionKey(context)
        if(key.isNullOrEmpty()) {
            encryptReceivedMessages.isEnabled = false
        } else {
            encryptionKey.setText(key.trim())
        }

        encryptionKey.doAfterTextChanged{
            if (it == null || it.toString().isEmpty()) {
                Settings.setEncryptionKey(context, null)
                Settings.setEncryptReceivedMessages(context, false)
                encryptReceivedMessages.isChecked = false
                encryptReceivedMessages.isEnabled = false
            } else {
                encryptReceivedMessages.isEnabled = true
                Settings.setEncryptionKey(context, it.toString().trim())
            }
        }

        encryptReceivedMessages.isChecked = Settings.encryptReceivedMessages(context)
        encryptReceivedMessages.setOnCheckedChangeListener{ _, isChecked -> run {
            Settings.setEncryptReceivedMessages(context, isChecked)
        }}
    }

    private fun registerListeners() {
        appToolbar().setOnClickListener { onBackClicked() }
        findViewById<MaterialButton>(R.id.settingsLogoutButton).setOnClickListener { onLogoutClick() }
    }

    private fun onBackClicked() {
        Timber.d("back button clicked")
        redirectToMain()
    }

    private fun redirectToMain() {
        finish()
        val switchActivityIntent = Intent(this, MainActivity::class.java)
        startActivity(switchActivityIntent)
    }

    private fun appToolbar(): MaterialToolbar {
        return findViewById(R.id.settings_toolbar)
    }

    private fun requestReadCallLogPermission(context: Context) {
        if(!Settings.isLoggedIn(context)) {
            return
        }
        Timber.d("requesting permissions")
        val requestPermissionLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { permissions ->
            permissions.entries.forEach {
                Timber.d("${it.key} = ${it.value}")
            }
        }
        val permissions = arrayOf(
            Manifest.permission.READ_CALL_LOG,
            Manifest.permission.READ_PHONE_STATE
        )

        requestPermissionLauncher.launch(permissions)
        Timber.d("creating permissions launcher")
    }

    private fun onLogoutClick() {
        Timber.d("logout button clicked")
        MaterialAlertDialogBuilder(this)
            .setTitle("Confirm")
            .setMessage("Are you sure you want to logout of the httpSMS App?")
            .setNeutralButton("Cancel"){ _, _ -> Timber.d("logout dialog canceled") }
            .setPositiveButton("Logout"){_, _ ->
                Timber.d("logging out user")
                Settings.setApiKeyAsync(this, null)
                Settings.setSIM1PhoneNumber(this, null)
                Settings.setSIM2PhoneNumber(this, null)
                Settings.setActiveStatusAsync(this, true, Constants.SIM1)
                Settings.setActiveStatusAsync(this, true, Constants.SIM2)
                Settings.setIncomingActiveSIM1(this, true)
                Settings.setIncomingActiveSIM2(this, true)
                Settings.setUserID(this, null)
                Settings.setEncryptionKey(this, null)
                Settings.setEncryptReceivedMessages(this, false)
                Settings.setFcmTokenLastUpdateTimestampAsync(this, 0)
                redirectToLogin()
            }
            .show()
    }

    private fun redirectToLogin():Boolean {
        if (Settings.isLoggedIn(this)) {
            return false
        }
        val switchActivityIntent = Intent(this, LoginActivity::class.java)
        startActivity(switchActivityIntent)
        return true
    }
}
