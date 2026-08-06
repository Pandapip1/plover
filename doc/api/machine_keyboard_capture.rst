``plover.machine.keyboard_capture`` -- Keyboard capture
================================================================

.. automodule:: plover.machine.keyboard_capture
   :no-members:

.. autoclass:: plover.machine.keyboard_capture.Capture

   .. automethod:: start

   .. automethod:: cancel

   .. automethod:: suppress

   The following methods are available to implementors to hook into the
   keyboard capture system:

   .. automethod:: key_down

   .. automethod:: key_up

   The following classmethods make up the plugin interface:

   .. automethod:: is_supported

   .. automethod:: get_missing_requirements

   .. automethod:: is_available

   .. automethod:: get_option_info

   .. automethod:: create

   .. autoattribute:: AUTOMATIC_PRIORITY

.. autoclass:: plover.machine.keyboard_capture.AutomaticCapture

   Always registered under the name ``Automatic``, the default value of the
   ``keyboard_capture_type`` configuration option.

.. autofunction:: plover.machine.keyboard_capture.resolve_keyboard_capture

.. autofunction:: plover.machine.keyboard_capture.get_active_keyboard_capture

.. autofunction:: plover.machine.keyboard_capture.set_active_keyboard_capture
