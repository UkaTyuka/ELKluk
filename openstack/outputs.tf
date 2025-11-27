output "elk_public_ip" {
  value = openstack_networking_floatingip_v2.elk_fip.address
}
