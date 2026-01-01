/**
 * Settings Page
 * User preferences and configuration
 */

import { useState, useEffect } from 'react';
import { Save, Settings as SettingsIcon, Palette, Bell, FileText, Music } from 'lucide-react';
import axios from 'axios';
import useStore from '../store';
import { Card, Button, Input, Badge } from '../components';

const SettingsPage = () => {
  const settings = useStore((state) => state.settings);
  const updateSettings = useStore((state) => state.updateSettings);
  const addNotification = useStore((state) => state.addNotification);

  const [formData, setFormData] = useState(settings);
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  useEffect(() => {
    const changed = JSON.stringify(formData) !== JSON.stringify(settings);
    setHasChanges(changed);
  }, [formData, settings]);

  const handleChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);

    try {
      const response = await axios.patch('/api/settings', formData);
      updateSettings(response.data.settings);

      addNotification({
        type: 'success',
        message: 'Settings saved successfully'
      });

      setHasChanges(false);
    } catch (error) {
      console.error('Error saving settings:', error);
      addNotification({
        type: 'error',
        message: 'Failed to save settings'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(settings);
    setHasChanges(false);
  };

  const themes = [
    { id: 'dark', name: 'Dark', color: '#0a0a0f' },
    { id: 'midnight', name: 'Midnight', color: '#000000' },
    { id: 'purple', name: 'Purple Haze', color: '#1a0a2e' }
  ];

  const styles = [
    { id: 'edm', name: 'EDM' },
    { id: 'lofi', name: 'Lo-Fi' },
    { id: 'trap', name: 'Trap' },
    { id: 'hiphop', name: 'Hip-Hop' },
    { id: 'ambient', name: 'Ambient' },
    { id: 'rock', name: 'Rock' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-accent" />
            Settings
          </h1>
          <p className="text-gray-400 mt-2">Configure your MashDeck preferences</p>
        </div>

        {hasChanges && (
          <Badge variant="warning">Unsaved Changes</Badge>
        )}
      </div>

      {/* Appearance Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Palette className="w-5 h-5 text-accent" />
          <h2 className="text-xl font-bold">Appearance</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Theme</label>
            <div className="grid grid-cols-3 gap-3">
              {themes.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleChange('theme', theme.id)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.theme === theme.id
                      ? 'border-accent bg-accent/10'
                      : 'border-white/10 hover:border-white/20'
                  }`}
                >
                  <div
                    className="w-full h-12 rounded mb-2"
                    style={{ backgroundColor: theme.color }}
                  />
                  <p className="font-medium">{theme.name}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Notifications Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Bell className="w-5 h-5 text-accent" />
          <h2 className="text-xl font-bold">Notifications</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
            <div>
              <p className="font-medium">Enable Notifications</p>
              <p className="text-sm text-gray-400">Receive updates about generations and events</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.notifications_enabled}
                onChange={(e) => handleChange('notifications_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Project Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-5 h-5 text-accent" />
          <h2 className="text-xl font-bold">Project Defaults</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
            <div>
              <p className="font-medium">Auto-Save</p>
              <p className="text-sm text-gray-400">Automatically save projects</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.auto_save}
                onChange={(e) => handleChange('auto_save', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
            </label>
          </div>
        </div>
      </Card>

      {/* Music Defaults */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Music className="w-5 h-5 text-accent" />
          <h2 className="text-xl font-bold">Music Defaults</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Default Style</label>
            <div className="grid grid-cols-3 gap-2">
              {styles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => handleChange('default_style', style.id)}
                  className={`p-3 rounded-lg border transition-all ${
                    formData.default_style === style.id
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-white/10 hover:border-white/20'
                  }`}
                >
                  {style.name}
                </button>
              ))}
            </div>
          </div>

          <Input
            label="Default BPM"
            type="number"
            min="60"
            max="200"
            value={formData.default_bpm}
            onChange={(e) => handleChange('default_bpm', parseInt(e.target.value))}
          />
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <Button
          variant="ghost"
          onClick={handleReset}
          disabled={!hasChanges || loading}
        >
          Reset
        </Button>
        <Button
          onClick={handleSave}
          disabled={!hasChanges || loading}
          loading={loading}
          icon={<Save className="w-5 h-5" />}
        >
          Save Settings
        </Button>
      </div>
    </div>
  );
};

export default SettingsPage;
