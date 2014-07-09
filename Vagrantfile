# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty64"

  config.vm.provider "virtualbox" do |v|
    v.customize(
      ['createhd',
       '--filename', 'vagrant0.vhd',
       '--size', 32])
    v.customize(
      ['storageattach',
       :id,
       '--storagectl', 'SATAController',
       '--port', 1,
       '--device', 0,
       '--type', 'hdd',
       '--medium',
       'vagrant0.vhd'])
  end
end
