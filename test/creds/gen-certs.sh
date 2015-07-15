rm -rf deploy/trusted/
mkdir tmp/ deploy/trusted/ deploy/trusted/certs/ deploy/trusted/cert_keys/ deploy/trusted/crl/
if [ -z "$1" ]
then
python src/vendor/geni_trust/gen-certs.py tmp/
else
python src/vendor/geni_trust/gen-certs.py tmp/ --authority $1
fi
cp tmp/ca-cert.pem deploy/trusted/certs/
cp tmp/ca-key.pem deploy/trusted/cert_keys/
cp tmp/sa-cert.pem deploy/trusted/certs/
cp tmp/sa-key.pem deploy/trusted/cert_keys/
cp tmp/ma-cert.pem deploy/trusted/certs/
cp tmp/ma-key.pem deploy/trusted/cert_keys/
cp tmp/ch-cert.pem deploy/trusted/certs/
cp tmp/ch-key.pem deploy/trusted/cert_keys/
cp tmp/root-*.pem admin/
cp tmp/*.pem test/creds/
cp tmp/*.xml test/creds/
rm -rf tmp/
