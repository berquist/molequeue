/******************************************************************************

  This source file is part of the MoleQueue project.

  Copyright 2012 Kitware, Inc.

  This source code is released under the New BSD License, (the "License").

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

******************************************************************************/

#ifndef ABSTRACTRPCINTERFACE_H
#define ABSTRACTRPCINTERFACE_H

#include <QtCore/QObject>

#include <molequeue/molequeueglobal.h>
#include <molequeue/transport/message.h>

#include "mqconnectionexport.h"

class AbstractRpcInterfaceTest;

namespace Json
{
class Value;
}

namespace MoleQueue
{
class JsonRpc;
class Connection;
class Message;

/**
 * @class AbstractRpcInterface abstractrpcinterface.h <molequeue/abstractrpcinterface.h>
 * @brief Bridge between application and JSON-RPC interprocess communication.
 * @author David C. Lonie
 */
class MQCONNECTION_EXPORT AbstractRpcInterface : public QObject
{
  Q_OBJECT
public:
  /**
   * Constructor.
   *
   * @param parentObject The parent object
   */
  explicit AbstractRpcInterface(QObject *parentObject = NULL);

  /**
   * Destructor.
   */
  virtual ~AbstractRpcInterface();

  friend class ::AbstractRpcInterfaceTest;

protected slots:

  /**
   * Interpret a newly received message.
   *
   * @param msg The new Message object.
   */
  void readMessage(const MoleQueue::Message msg);

  /**
   * Send a response indicating that an invalid packet (unparsable) has been
   * received.
   *
   * @param request The invalid Message.
   * @param errorDataObject The Json::Value to be used as the error data.
   */
  void replyToInvalidMessage(const MoleQueue::Message &request,
                             const Json::Value &errorDataObject);

  /**
   * Send a response indicating that an invalid request has been
   * received.
   *
   * @param request The invalid Message.
   * @param errorDataObject The Json::Value to be used as the error data.
   */
  void replyToInvalidRequest(const MoleQueue::Message &request,
                             const Json::Value &errorDataObject);

  /**
   * Send a response indicating that an unknown method has been requested.
   *
   * @param request The invalid Message.
   * @param errorDataObject The Json::Value to be used as the error data.
   */
  void replyToUnrecognizedRequest(const MoleQueue::Message &request,
                                  const Json::Value &errorDataObject);

  /**
   * Send a response indicating that a request with invalid parameters has been
   * received.
   *
   * @param request The invalid Message.
   * @param errorDataObject The Json::Value to be used as the error data.
   */
  void replyToinvalidRequestParams(const MoleQueue::Message &request,
                                   const Json::Value &errorDataObject);

  /**
   * Send a response indicating that an internal error has occurred.
   *
   * @param request The invalid Message.
   * @param errorDataObject The Json::Value to be used as the error data.
   */
  void replyWithInternalError(const MoleQueue::Message &request,
                              const Json::Value &errorDataObject);

protected:

  /// Set the JsonRpc object for this interface.
  virtual void setJsonRpc(JsonRpc *jsonrpc);

  /**
   * Call this function to get an ID for the next request.
   * @return The next Message id generator.
   */
  MessageIdType nextMessageId();

  /// The internal JsonRpc object
  JsonRpc *m_jsonrpc;

private:
  /// Counter for packet requests
  IdType m_messageIdGenerator;
};

} // end namespace MoleQueue

#endif // ABSTRACTRPCINTERFACE_H
