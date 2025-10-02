import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { DeleteFieldLevelEncryptionConfigRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteFieldLevelEncryptionConfigCommandInput
  extends DeleteFieldLevelEncryptionConfigRequest {}
export interface DeleteFieldLevelEncryptionConfigCommandOutput
  extends __MetadataBearer {}
export declare class DeleteFieldLevelEncryptionConfigCommand extends $Command<
  DeleteFieldLevelEncryptionConfigCommandInput,
  DeleteFieldLevelEncryptionConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteFieldLevelEncryptionConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteFieldLevelEncryptionConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteFieldLevelEncryptionConfigCommandInput,
    DeleteFieldLevelEncryptionConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
