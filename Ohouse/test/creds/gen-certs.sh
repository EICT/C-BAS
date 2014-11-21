mkdir tmp/ deploy/trusted/ deploy/trusted/certs/ deploy/trusted/cert_keys/ deploy/trusted/crl/
python src/vendor/geni_trust/gen-certs.py tmp/
cp tmp/ca-cert.pem deploy/trusted/certs/
cp tmp/ca-key.pem deploy/trusted/cert_keys/
cp tmp/sa-cert.pem deploy/trusted/certs/
cp tmp/sa-key.pem deploy/trusted/cert_keys/
cp tmp/ma-cert.pem deploy/trusted/certs/
cp tmp/ma-key.pem deploy/trusted/cert_keys/
cp tmp/root-*.pem admin/
cp tmp/*.pem test/creds/
cp tmp/*.xml test/creds/
rm -rf tmp/
