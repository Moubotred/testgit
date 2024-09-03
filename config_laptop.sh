#!/bin/bash

# Script para configurar la laptop para que siga funcionando con la tapa cerrada
# y la pantalla apagada, y revertir los cambios cuando sea necesario.

ACTION="$1"

function set_energy_settings {
    echo "Configurando ajustes de energía..."
    sudo sed -i 's/^HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf
    sudo sed -i 's/^HandleLidSwitchDocked=.*/HandleLidSwitchDocked=ignore/' /etc/systemd/logind.conf
    sudo sed -i 's/^HandleLidSwitchExternalPower=.*/HandleLidSwitchExternalPower=ignore/' /etc/systemd/logind.conf
    sudo systemctl restart systemd-logind
    echo "Ajustes de energía configurados."
}

function unset_energy_settings {
    echo "Revirtiendo ajustes de energía..."
    sudo sed -i 's/^HandleLidSwitch=ignore/HandleLidSwitch=suspend/' /etc/systemd/logind.conf
    sudo sed -i 's/^HandleLidSwitchDocked=ignore/HandleLidSwitchDocked=suspend/' /etc/systemd/logind.conf
    sudo sed -i 's/^HandleLidSwitchExternalPower=ignore/HandleLidSwitchExternalPower=suspend/' /etc/systemd/logind.conf
    sudo systemctl restart systemd-logind
    echo "Ajustes de energía revertidos."
}

function set_display_settings {
    echo "Desactivando apagado de pantalla..."
    xset s off
    xset -dpms
    echo "Apagado de pantalla desactivado."
}

function unset_display_settings {
    echo "Reactivando apagado de pantalla..."
    xset s on
    xset +dpms
    echo "Apagado de pantalla reactivado."
}

case $ACTION in
    configure)
        set_energy_settings
        set_display_settings
        ;;
    revert)
        unset_energy_settings
        unset_display_settings
        ;;
    *)
        echo "Uso: $0 {configure|revert}"
        exit 1
        ;;
esac
