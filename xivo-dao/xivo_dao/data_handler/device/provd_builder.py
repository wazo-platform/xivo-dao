
PROVD_KEYS = [
    'id',
    'ip',
    'mac',
    'sn',
    'plugin',
    'vendor',
    'model',
    'version',
    'description',
]


def build_create(device):
    provd_device = _create_provd_device(device)
    provd_config = _create_provd_config(device)

    return (provd_device, provd_config)


def _create_provd_device(device):
    parameters = _filter_device_parameters(device)

    parameters['config'] = device.id

    if 'mac' in parameters:
        parameters['mac'] = parameters['mac'].lower()

    return parameters


def _filter_device_parameters(device):
    parameters = {}

    for key in PROVD_KEYS:
        if hasattr(device, key):
            parameters[key] = getattr(device, key)

    return parameters


def _create_provd_config(device):
    parameters = {
        'id': device.id,
        'deletable': True,
        'parent_ids': _build_parent_ids(device),
        'configdevice': getattr(device, 'template_id', 'defaultconfigdevice'),
        'raw_config': {}
    }

    return parameters


def _build_parent_ids(device):
    parent_ids = ['base', getattr(device, 'template_id', 'defaultconfigdevice')]
    return parent_ids


#def update_provd(self, provd_device, provd_config=None):
#    self._update_provd_device(provd_device)
#    self._update_provd_config(provd_config)
#
#def _update_provd_device(self, provd_device):
#    provd_device.update(self.to_provd_device())
#
#def _update_provd_config(self, provd_config):
#    if not provd_config:
#        return
#
#    parent_ids = provd_config.pop('parent_ids', [])
#    raw_config = provd_config.pop('raw_config', {})
#
#    if 'configdevice' in provd_config:
#        self._remove_old_configdevice(provd_config['configdevice'], parent_ids)
#
#    self._update_base_config(provd_config)
#    provd_config['parent_ids'] = self._update_parent_ids(parent_ids)
#    provd_config['raw_config'] = self._update_raw_config(raw_config)
#
#def _remove_old_configdevice(self, configdevice, parent_ids):
#    if configdevice in parent_ids:
#        parent_ids.remove(configdevice)
#
#def _update_base_config(self, provd_config):
#    provd_config['configdevice'] = self.get_template_id()
#
#def _update_parent_ids(self, parent_ids):
#    parent_ids = list(parent_ids)
#    template_id = self.get_template_id()
#    if template_id not in parent_ids:
#        parent_ids.append(template_id)
#    return parent_ids
#
#def _update_raw_config(self, raw_config):
#    return raw_config
