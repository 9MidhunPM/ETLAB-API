"""
Diagnostic endpoints for troubleshooting deployment issues
"""
from flask import Blueprint, jsonify
import socket
import dns.resolver
from app.config.config import config

diagnostic_bp = Blueprint('diagnostic', __name__, url_prefix='/api/diagnostic')

@diagnostic_bp.route('/dns-test', methods=['GET'])
def test_dns():
    """
    Test DNS resolution for the target host
    Useful for debugging network/DNS issues on different hosting platforms
    """
    target_host = 'etlab.kem.edu.in'
    results = {
        'target': target_host,
        'system_dns': None,
        'public_dns': None,
        'socket_resolution': None
    }
    
    # Test 1: System DNS resolution
    try:
        answers = socket.getaddrinfo(target_host, 443, socket.AF_INET, socket.SOCK_STREAM)
        if answers:
            results['system_dns'] = {
                'success': True,
                'ip': answers[0][4][0],
                'method': 'socket.getaddrinfo'
            }
    except Exception as e:
        results['system_dns'] = {
            'success': False,
            'error': str(e)
        }
    
    # Test 2: Public DNS resolution using dnspython
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # Google and Cloudflare DNS
        resolver.timeout = 5
        resolver.lifetime = 10
        
        answers = resolver.resolve(target_host, 'A')
        if answers:
            results['public_dns'] = {
                'success': True,
                'ips': [str(answer) for answer in answers],
                'nameservers': resolver.nameservers
            }
    except Exception as e:
        results['public_dns'] = {
            'success': False,
            'error': str(e)
        }
    
    # Test 3: Try socket.gethostbyname as fallback
    try:
        ip = socket.gethostbyname(target_host)
        results['socket_resolution'] = {
            'success': True,
            'ip': ip,
            'method': 'socket.gethostbyname'
        }
    except Exception as e:
        results['socket_resolution'] = {
            'success': False,
            'error': str(e)
        }
    
    # Determine overall status
    any_success = (
        (results['system_dns'] and results['system_dns'].get('success')) or
        (results['public_dns'] and results['public_dns'].get('success')) or
        (results['socket_resolution'] and results['socket_resolution'].get('success'))
    )
    
    return jsonify({
        'success': any_success,
        'message': f'DNS resolution {"successful" if any_success else "failed"} for {target_host}',
        'results': results
    }), 200 if any_success else 500

@diagnostic_bp.route('/network-info', methods=['GET'])
def network_info():
    """
    Get basic network information about the server environment
    """
    info = {
        'hostname': socket.gethostname(),
        'default_dns_servers': dns.resolver.default_resolver.nameservers[:5],
    }
    
    # Try to get outbound IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        info['outbound_ip'] = s.getsockname()[0]
        s.close()
    except Exception:
        info['outbound_ip'] = 'Unable to determine'
    
    return jsonify({
        'success': True,
        'info': info
    })
