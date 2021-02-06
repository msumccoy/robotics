dir=$(pwd)
mount="ram_disk"
ramdisk_name="system_ramdisk"
#
if grep -qs "$mount" /proc/mounts;then
  echo "mounted"
else
  mkdir "$mount"
  sudo mount -t tmpfs -o size=2048M "$ramdisk_name" "$dir/$mount"
#  sudo mount -t tmpfs -o size=1024M "$ramdisk_name" "$dir/$mount"
  echo "$ramdisk_name has been mounted on $dir/$mount"
fi
echo "script complete"
# line to put in fstab
# {ramdisk_name} {ramdisk_location} tmpfs rw, size=1024M 0 0
